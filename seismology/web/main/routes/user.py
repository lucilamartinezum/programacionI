from flask import Blueprint, render_template, current_app, redirect, url_for
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root
from ..forms.user_form import UserForm, UserEdit

import requests, json

user = Blueprint("user", __name__, url_prefix="/user")
# default_breadcrumb_root(user, ".main")

@user.route("/")
@register_breadcrumb(user, '.', 'Users')
def index():
    r = requests.get(current_app.config["API_URL"]+"/users",headers={"content-type":"application/json"})
    users = json.loads(r.text)['Users']
    title = "Users List"
    return render_template("users.html", title=title, users=users) # Mostrar template

@user.route("/add-user", methods=["GET", "POST"])
@register_breadcrumb(user, ".add", "Add User")
def create():
    form = UserForm() # Instanciar formulario
    if form.validate_on_submit(): # Si el formulario ha sido enviado y es valido correctamente
        user = {
            "email": form.email.data,
            "password": form.password.data,
            "admin": form.admin.data
        }
        data = json.dumps(user)
        print(data)
        r = requests.post(current_app.config["API_URL"]+"/users",headers={"content-type":"application/json"}, data=data)
        print(r)
        return redirect(url_for("user.index")) # Redirecciona a la lista
    return render_template("user_form.html", form=form)

@user.route("/edit/<int:id>", methods=["GET","POST"])
@register_breadcrumb(user, ".edit", "Edit User")
def edit(id):
    form = UserEditForm()
    url = current_app.config["API_URL"]+"/user/"+str(id)
    if not form.is_submitted():
        r = requests.get(url, headers={"content-type":"application/json"})
        if (r.status_code == 404):
            flash("User not found","danger")
            return redirect(url_for("user.index"))
        user = json.loads(r.text)
        form.email.data = user["email"]
        form.admin.data = user["admin"]

    if form.validate_on_submit():
        user = {
            "email": form.email.data,
            "admin": form.admin.data
        }
        data = json.dumps(user)
        r = requests.put(url, headers={"content-type":"application/json"}, data=data)
        flash("User edited","success")
        return redirect(url_for("user.index"))
    return render_template("user-edit.html", form=form, id=id)


@user.route('/user/delete/<int:id>')
def delete_user(id):
    url = current_app.config["API_URL"] + "/user/" + str(id)
    requests.delete(url=url, headers={'content-type': 'application/json'})
    return redirect(url_for('user.index'))


