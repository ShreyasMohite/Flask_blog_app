from flaskblog.models import User,Post,UserSchema,PostSchema
import secrets,os
from flask import render_template,url_for,redirect,flash,request,session,abort,jsonify
from flaskblog.forms import RegisterForm,LoginForm,ProfileUpdateForm,PostForm,UpdatePostForm,RequestResetForm,ResetPasswordForm
from flaskblog import app,db,bcrypt,mail
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message

@app.route("/")
@app.route("/home",methods=['GET','POST'])
@login_required
def Home():
    page=request.args.get('page',1,type=int)
    posts=Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=3)
    return render_template("home.html",posts=posts)


@app.route("/login",methods=['GET','POST'])
def Login():
    if current_user.is_authenticated:
        return redirect(url_for('Home'))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember_me.data)
            flash("You have logged In")
            next_page=request.args.get('next')
            return redirect (next_page) if next_page else redirect(url_for('Home'))
        else:
            flash("Incorrect email and password")

    return render_template("login.html",form=form)


@app.route("/register",methods=['GET','POST'])
def Register():
    if current_user.is_authenticated:
        return redirect(url_for('Home'))
    form=RegisterForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        username=form.username.data
        email=form.email.data
        password=hashed_password
        mydata=User(username,email,password)
        db.session.add(mydata)
        db.session.commit()
        flash("Your account has been created please login")
        return redirect(url_for('Login'))
    return render_template("register.html",form=form)





@app.route("/profile")
@login_required
def Profile(): 
    image_file=url_for('static',filename="pictures/"+current_user.image_file)
    return render_template("profile.html",image_file=image_file)


def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.path.splitext(form_picture.filename)
    picture_fn=random_hex+f_ext
    picture_path=os.path.join(app.root_path,'static/pictures',picture_fn)
    form_picture.save(picture_path)
    return picture_fn




@app.route("/profile/update",methods=['GET','POST'])
@login_required
def Profileupdate():
    form=ProfileUpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file=save_picture(form.picture.data)
            current_user.image_file=picture_file
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash("User Updated successfully")
        return redirect(url_for('Profile'))

    elif request.method=="GET":
        form.username.data=current_user.username
        form.email.data=current_user.email

    image_file=url_for('static',filename="pictures/"+current_user.image_file)

    return render_template("profileupdate.html",image_file=image_file,form=form)




@app.route("/logout")
def Logout():
    logout_user()
    return redirect(url_for('Login'))


@app.route("/post/new",methods=['GET','POST'])
@login_required
def post():
    form=PostForm()
    if form.validate_on_submit():
        mydatas=Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(mydatas)
        db.session.commit()
        flash("Your post is created succesfully")
        return redirect(url_for('Home'))

    posts=Post.query.all()
    return render_template("posts.html",form=form,posts=posts)



@app.route("/post/<int:post_id>")
def PostId(post_id):
    post=Post.query.get_or_404(post_id)
    return render_template("postid.html",title="post",post=post)




@app.route("/post/<int:user_id>")
def PostUser(user_id):
    post=User.query.get_or_404(user_id)
    return render_template("postid.html",title="post",post=post)



@app.route("/post/<int:post_id>/updates",methods=['GET','POST'])
@login_required
def updatepost(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author!=current_user:
        abort(403)
    form=UpdatePostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data
        db.session.commit()
        flash("Post is updated")
        return redirect(url_for('Home'))
    elif request.method=="GET":
        form.title.data=post.title
        form.content.data=post.content
    return render_template("updatepost.html",title="Update",post=post,form=form)


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('Home'))




@app.route("/user/<username>",methods=['GET','POST'])
@login_required
def Username(username):
    page=request.args.get('page',1,type=int)
    user=User.query.filter_by(username=username).first_or_404()
    posts=Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page,per_page=3)
    return render_template("userpost.html",posts=posts,user=user)





def send_reset_email(user):
    token=user.get_reset_token()
    msg=Message("Password Reset Request",sender="youremail",recipients=[user.email])

    msg.body = f'''To reset your password visit this link:
{url_for('reset_token',token=token,_external=True)}

Please follow this link for reset your password.
'''
    mail.send(msg)





@app.route("/request",methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        redirect(url_for('Home'))
    form=RequestResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent to your email to reset your password")
        return redirect(url_for('Login'))
    return render_template("request.html",title="Request",form=form)






@app.route("/reset_password/<token>",methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('Home'))
    user=User.verify_reset_token(token)
    if user is None:
        flash("That is invalid or expire token")
        return redirect(url_for('reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password=hashed_password
        db.session.commit()
        flash("Your has been updated")
        return redirect(url_for('Login'))
    return render_template("reset.html",title="Request",form=form)






@app.route("/user/api")
@login_required
def userapis():
    user=User.query.all()
    user_schema=UserSchema(many=True)
    output=user_schema.dump(user)
    return jsonify(output)



@app.route("/post/api")
@login_required
def postapis():
    user=Post.query.all()
    post_schema=PostSchema(many=True)
    output=post_schema.dump(user)
    return jsonify(output)


