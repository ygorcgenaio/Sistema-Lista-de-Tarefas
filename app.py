from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Tarefa
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_segura' # Necessário para usar flash()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tarefas.db'

db.init_app(app)

# GARANTE QUE O BANCO DE DADOS SEJA CRIADO ASSIM QUE O RENDER LIGAR O SISTEMA
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Rota principal que exibe a tabela de tarefas"""
    # Busca todas as tarefas ordenadas para mostrar na tabela
    tarefas = Tarefa.query.order_by(Tarefa.ordem_apresentacao).all()
    # Calcula o total para o rodapé da tabela
    total = sum(t.custo for t in tarefas)
    return render_template('index.html', tarefas=tarefas, total=total)

@app.route('/incluir', methods=['GET', 'POST'])
def incluir():
    """Rota para cadastrar novas tarefas"""
    if request.method == 'POST':
        nome = request.form['nome']
        custo = float(request.form['custo'])
        data_limite = datetime.strptime(request.form['data_limite'], '%Y-%m-%d').date()

        # Validação: Nome único
        if Tarefa.query.filter_by(nome=nome).first():
            flash('Erro: Já existe uma tarefa com este nome.')
            return redirect(url_for('incluir'))

        # Lógica de Ordem: Pega o maior valor atual e soma 1
        ultima_ordem = db.session.query(db.func.max(Tarefa.ordem_apresentacao)).scalar() or 0
        
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
    """Rota para remover uma tarefa"""
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
    """Rota para editar dados de uma tarefa existente"""
    tarefa = Tarefa.query.get_or_404(id)
    
    if request.method == 'POST':
        novo_nome = request.form['nome']
        novo_custo = float(request.form['custo'])
        nova_data = datetime.strptime(request.form['data_limite'], '%Y-%m-%d').date()

        # Validação: Verifica duplicidade de nome ignorando a própria tarefa
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
    # Busca a tarefa imediatamente acima na ordem
    tarefa_cima = Tarefa.query.filter(Tarefa.ordem_apresentacao < tarefa_atual.ordem_apresentacao)\
                               .order_by(Tarefa.ordem_apresentacao.desc()).first()
    
    if tarefa_cima:
        # Troca as ordens de apresentação entre as duas
        ordem_aux = tarefa_atual.ordem_apresentacao
        tarefa_atual.ordem_apresentacao = tarefa_cima.ordem_apresentacao
        tarefa_cima.ordem_apresentacao = ordem_aux
        db.session.commit()
    
    # O segredo: redirecionar para a função 'index' (que é a rota '/')
    return redirect(url_for('index'))

@app.route('/descer/<int:id>')
def descer(id):
    tarefa_atual = Tarefa.query.get_or_404(id)
    # Busca a tarefa imediatamente abaixo na ordem
    tarefa_baixo = Tarefa.query.filter(Tarefa.ordem_apresentacao > tarefa_atual.ordem_apresentacao)\
                                 .order_by(Tarefa.ordem_apresentacao.asc()).first()
    
    if tarefa_baixo:
        # Troca as ordens de apresentação entre as duas
        ordem_aux = tarefa_atual.ordem_apresentacao
        tarefa_atual.ordem_apresentacao = tarefa_baixo.ordem_apresentacao
        tarefa_baixo.ordem_apresentacao = ordem_aux
        db.session.commit()
        
    return redirect(url_for('index'))
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
