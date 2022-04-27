from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms.user_form import RegisterForm, LoginForm
from data.hokky import Hokky
from forms.hokky_form import HokkyForm
from data.user import User
from data import db_session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'sisters_of_silence'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def face():
    return render_template('face.html', )


@app.route('/profile')
@login_required
def prof():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == current_user.email)
    u = user[0]
    if u.pic:
        with open(f'static/img/{u.id}.jpg', mode='wb') as w:
            w.write(u.pic)
        return render_template('profile.html', user=u, img=f'static/img/{u.id}.jpg')
    return render_template('profile.html', user=u, img='static/img/alica.jpg')


@app.route('/edit_prof', methods=['POST', 'GET'])
@login_required
def edit_prof():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == current_user.email)
    u = user[0]
    if request.method == 'GET':
        if u.pic:
            with open(f'static/img/{u.id}.jpg', mode='wb') as w:
                w.write(u.pic)
            return render_template('edit_profile.html', user=u, img=f'static/img/{u.id}.jpg')
        return render_template('edit_profile.html', user=u, img='static/img/alica.jpg')
    elif request.method == 'POST':
        f = request.files['file']
        c = f.read()
        name = request.form['name']
        email = request.form['email']
        if name:
            u.name = name
            current_user.name = name
        if email:
            if db_sess.query(User).filter(User.email == email).first():
                if u.pic:
                    with open(f'static/img/{u.id}.jpg', mode='wb') as w:
                        w.write(u.pic)
                    return render_template('edit_profile.html', user=u, img=f'static/img/{u.id}.jpg', message="Такой пользователь уже есть")
                return render_template('edit_profile.html', user=u, img='static/img/alica.jpg', message="Такой пользователь уже есть")
            u.email = email
        if c:
            u.pic = c
        db_sess.commit()
        try:
            with open(f'static/img/{u.id}.jpg', mode='wb') as w:
                w.write(u.pic)
            return render_template('profile.html', user=u, img=f'static/img/{u.id}.jpg')
        except Exception:
            return render_template('profile.html', user=u, img='static/img/alica.jpg')


@app.route('/index/<int:id>')
def index(id):
    db_sess = db_session.create_session()
    content = db_sess.query(Hokky)
    user = db_sess.query(User)
    if id == 1:
        con = content[:6]
    else:
        con = content[6 * (id - 1): 6 * id]
    c = list(content)
    mnozh = 1
    while True:
        if len(c) <= 6 * mnozh:
            break
        else:
            mnozh += 1
    return render_template('index.html', content=con, users=user, pages=mnozh, active=id)


@app.route('/leader_board')
def lead_bord():
    return render_template('leader.html')


@app.route('/registration', methods=['GET', 'POST'])
def registr():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('reg.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('reg.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('reg.html', title='Регистрация', form=form)


@app.route('/guide')
def gui():
    return render_template('guide.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/stix',  methods=['GET', 'POST'])
@login_required
def add_stix():
    form = HokkyForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        stix = Hokky()
        stix.content = form.content.data
        if len(stix.content.split()) == 3:
            stix.user_name = current_user.name
            current_user.hokky.append(stix)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        else:
            return render_template('stix.html', title='Создать пост',
                                   form=form, message='Длина не равна 3 строкам')
    return render_template('stix.html', title='Создать пост',
                           form=form)


@app.route('/prof_stixi/<int:id>',  methods=['GET', 'POST'])
@login_required
def prof_stixi(id):
    db_sess = db_session.create_session()
    content = db_sess.query(Hokky).filter(Hokky.user_id == current_user.id)
    user = db_sess.query(User).get(current_user.id)
    if id == 1:
        con = content[:5]
    else:
        con = content[5 * (id - 1): 5 * id]
    c = list(content)
    mnozh = 1
    while True:
        if len(c) <= 5 * mnozh:
            break
        else:
            mnozh += 1
    return render_template('user_index.html', content=con, users=user, pages=mnozh, active=id)


@app.route('/stix_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_stix(id):
    form = HokkyForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        stix = db_sess.query(Hokky).filter(Hokky.id == id).first()
        if stix:
            form.content.data = stix.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        stix = db_sess.query(Hokky).filter(Hokky.id == id).first()
        if stix:
            stix.content = form.content.data
            if len(stix.content.split()) == 3:
                db_sess.commit()
                return redirect('/prof_stixi/1')
            else:
                return render_template('stix.html', title='Редактирование',
                                       form=form, message='Длина не равна 3 строкам')
        else:
            abort(404)
    return render_template('stix.html',
                           title='Редактирование',
                           form=form
                           )


@app.route('/stix_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def stix_delete(id):
    db_sess = db_session.create_session()
    stix = db_sess.query(Hokky).filter(Hokky.id == id).first()
    if stix:
        db_sess.delete(stix)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/prof_stixi/1')


@app.route('/change_pass', methods=['GET', 'POST'])
@login_required
def change_pass():
    if request.method == "GET":
        return render_template('change_pass.html')

    if request.method == "POST":
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)
        print(request.form['1'])
        print(request.form['2'])
        if request.form['1'] == request.form['2']:
            user.set_password(request.form['1'])
            db_sess.commit()
            return redirect('/profile')
        return render_template('change_pass.html', message='Пароли не совпадают')


if __name__ == '__main__':
    main()