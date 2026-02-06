from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Tarefa(db.Model):
    __tablename__ = 'tarefas'
    
    # Atributos conforme a especificação técnica
    id = db.Column(db.Integer, primary_key=True) 
    nome = db.Column(db.String(200), nullable=False, unique=True) # Nome único
    custo = db.Column(db.Numeric(10, 2), nullable=False)         # Decimal >= 0
    data_limite = db.Column(db.Date, nullable=False)             # Data válida
    ordem_apresentacao = db.Column(db.Integer, nullable=False, unique=True) # Ordem única

    def __repr__(self):
        return f'<Tarefa {self.nome}>'