from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Tarefa
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_segura'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tarefas.db'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    tarefas = Tarefa.query.order_by(Tarefa.ordem_apresentacao).all()
    total = sum(t.custo for t in tarefas)
    return render_template('index.html', tarefas=tarefas, total=total)

@app.route('/incluir', methods=['GET', 'POST'])
def incluir():
    if request.method == 'POST':
        nome = request.form['nome']
        custo = float(request.form['custo'])
        data_limite = datetime.strptime(request.form['data_limite'], '%Y-%m-%d').date()

        if Tarefa.query.filter_by(nome=nome).first():
            flash('Erro: Já existe uma tarefa com este nome.')
            return redirect(url_for('incluir'))

        ultima_ordem = db.session.query(func.max(Tarefa.ordem_apresentacao)).scalar() or 0
        
        nova_tarefa = Tarefa(
            nome=nome,
            custo=custo,
            data_limite=data_limite,
            ordem_apresentacao=ultima_ordem + 1
        )
        
        db.session.add(nova_tarefa)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('incluir.html')

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    tarefa = Tarefa.query.get_or_404(id)
    try:
        db.session.delete(tarefa)
        db.session.commit()
    except:
        db.session.rollback()
        flash("Erro ao tentar excluir a tarefa.")
    return redirect(url_for('index'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    tarefa = Tarefa.query.get_or_404(id)
    if request.method == 'POST':
        novo_nome = request.form['nome']
        novo_custo = float(request.form['custo'])
        nova_data = datetime.strptime(request.form['data_limite'], '%Y-%m-%d').date()

        tarefa_existente = Tarefa.query.filter(Tarefa.nome == novo_nome, Tarefa.id != id).first()
        if tarefa_existente:
            flash('Erro: Já existe uma tarefa com este nome.')
            return redirect(url_for('editar', id=id))

        tarefa.nome = novo_nome
        tarefa.custo = novo_custo
        tarefa.data_limite = nova_data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('editar.html', tarefa=tarefa)

@app.route('/subir/<int:id>')
def subir(id):
    tarefa_atual = Tarefa.query.get_or_404(id)
    tarefa_cima = Tarefa.query.filter(Tarefa.ordem_apresentacao < tarefa_atual.ordem_apresentacao)\
                               .order_by(Tarefa.ordem_apresentacao.desc()).first()
    if tarefa_cima:
        ordem_original_atual = tarefa_atual.ordem_apresentacao
        ordem_original_cima = tarefa_cima.ordem_apresentacao
        
        tarefa_atual.ordem_apresentacao = 0
        db.session.commit()
        
        tarefa_cima.ordem_apresentacao = ordem_original_atual
        db.session.commit()
        
        tarefa_atual.ordem_apresentacao = ordem_original_cima
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/descer/<int:id>')
def descer(id):
    tarefa_atual = Tarefa.query.get_or_404(id)
    tarefa_baixo = Tarefa.query.filter(Tarefa.ordem_apresentacao > tarefa_atual.ordem_apresentacao)\
                                 .order_by(Tarefa.ordem_apresentacao.asc()).first()
    if tarefa_baixo:
        ordem_original_atual = tarefa_atual.ordem_apresentacao
        ordem_original_baixo = tarefa_baixo.ordem_apresentacao
        
        tarefa_atual.ordem_apresentacao = 0
        db.session.commit()
        
        tarefa_baixo.ordem_apresentacao = ordem_original_atual
        db.session.commit()
        
        tarefa_atual.ordem_apresentacao = ordem_original_baixo
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
