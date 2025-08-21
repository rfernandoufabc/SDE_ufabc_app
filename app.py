# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import base64
from alchemy_data import init_models


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sde_ufabc_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dados.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)
Campus, Curso, Entidade, Atributo, entidade_curso, entidade_atributo, Categoria, TipoAtividade, TipoParticipacao = init_models(db)

@app.cli.command('init-db')
def init_db_command():
    from alchemy_data import init_db
    init_db(app, db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        dados = {
            "curso": request.form['curso'],
            "periodo": request.form['periodo'],
            "atributos": request.form.getlist('atributos'),
            "categoria": request.form['categoria_id'],
            "tipo_atividade": request.form['tipo_atividade'],
            "tipo_participacao": request.form['tipo_participacao']
        }
        return redirect(url_for('resultado', **dados))

    from alchemy_data import (CATEGORIAS,
                              ATV_PRATICAS, ATV_TEORICAS, ATV_AMBAS,
                              PART_GRUPO, PART_INDIVIDUAL, PART_AMBOS)

    categorias_map = CATEGORIAS

    tipos_atividade_map = {
        ATV_PRATICAS: 'Práticas',
        ATV_TEORICAS: 'Teóricas',
        ATV_AMBAS: 'Ambas'
    }

    tipos_participacao_map = {
        PART_GRUPO: 'Grupo',
        PART_INDIVIDUAL: 'Individual',
        PART_AMBOS: 'Ambos'
    }

    todos_os_cursos = Curso.query.order_by('nome_curso').all()

    cursos_agrupados = {}
    for curso in todos_os_cursos:
        if curso.categoria not in cursos_agrupados:
            cursos_agrupados[curso.categoria] = []
        cursos_agrupados[curso.categoria].append(curso)

    todos_atributos = Atributo.query.order_by('nome').all()

    return render_template('form.html',
                         cursos_agrupados=cursos_agrupados,
                         todos_atributos=todos_atributos,
                         categorias=categorias_map.items(),
                         tipos_atividade=tipos_atividade_map.items(),
                         tipos_participacao=tipos_participacao_map.items())

@app.route('/resultado')
def resultado():
    curso_id = request.args.get('curso')
    periodo = request.args.get('periodo')
    atributos_ids = request.args.getlist('atributos')
    categoria = request.args.get('categoria')
    tipo_atividade = request.args.get('tipo_atividade')
    tipo_participacao = request.args.get('tipo_participacao')

    from alchemy_data import (CATEGORIAS,
                              ATV_PRATICAS, ATV_TEORICAS, ATV_AMBAS,
                              PART_GRUPO, PART_INDIVIDUAL, PART_AMBOS)

    categorias_id_map = {}
    for codigo, nome in CATEGORIAS.items():
        obj = Categoria.query.filter_by(nome=nome).first()
        if obj:
            categorias_id_map[codigo] = obj.id

    tipo_prat = TipoAtividade.query.filter_by(nome='Práticas').first()
    tipo_teo = TipoAtividade.query.filter_by(nome='Teóricas').first()
    tipo_amb = TipoAtividade.query.filter_by(nome='Ambas').first()
    tipos_atividade_id_map = {
        ATV_PRATICAS: (tipo_prat.id if tipo_prat else None),
        ATV_TEORICAS: (tipo_teo.id if tipo_teo else None),
        ATV_AMBAS: (tipo_amb.id if tipo_amb else None)
    }

    part_grp = TipoParticipacao.query.filter_by(nome='Grupo').first()
    part_ind = TipoParticipacao.query.filter_by(nome='Individual').first()
    part_amb = TipoParticipacao.query.filter_by(nome='Ambos').first()
    tipos_participacao_id_map = {
        PART_GRUPO: (part_grp.id if part_grp else None),
        PART_INDIVIDUAL: (part_ind.id if part_ind else None),
        PART_AMBOS: (part_amb.id if part_amb else None)
    }

    selected_categoria_id = categorias_id_map.get(categoria)
    selected_tipo_atividade_id = tipos_atividade_id_map.get(tipo_atividade)
    selected_tipo_participacao_id = tipos_participacao_id_map.get(tipo_participacao)

    curso = Curso.query.filter_by(id_curso=curso_id).first()
    campus = curso.campus if curso else None
    categoria_obj = Categoria.query.get(selected_categoria_id)
    tipo_atividade_obj = TipoAtividade.query.get(selected_tipo_atividade_id)
    tipo_participacao_obj = TipoParticipacao.query.get(selected_tipo_participacao_id)
    atributos_selecionados = [Atributo.query.get(int(aid)).nome for aid in atributos_ids]

    entidades = Entidade.query.all()
    afinidade_resultados = []

    for e in entidades:
        afinidade = {
            'atributos': 0,
            'curso': 0,
            'campus': 0,
            'categoria': 0,
            'tipo_atividade': 0,
            'tipo_participacao': 0,
            'total': 0
        }
        # Atributos: 50% no total, distribuídos entre os atributos encontrados (máx 10 atributos)
        atributos_entidade = [str(a.id) for a in e.atributos]
        match_atributos = len(set(atributos_ids) & set(atributos_entidade))
        afinidade['atributos'] = min(match_atributos * 5, 50)

        # Curso: 15%
        if curso and curso in e.cursos:
            afinidade['curso'] = 15

        # Campus: 10%
        if campus and e.campus_id == campus.id:
            afinidade['campus'] = 10

        # Categoria: 15%
        if selected_categoria_id and e.categoria_id == selected_categoria_id:
            afinidade['categoria'] = 15

        # Tipo Atividade: 5% se igual, 2.5% se compatibilidade parcial
        if selected_tipo_atividade_id and e.tipo_atividade_id == selected_tipo_atividade_id:
            afinidade['tipo_atividade'] = 5
        elif selected_tipo_atividade_id:
            tipo_atividade_ambas = TipoAtividade.query.filter_by(nome='Ambas').first()
            if tipo_atividade_ambas:
                if (e.tipo_atividade_id == tipo_atividade_ambas.id and selected_tipo_atividade_id != tipo_atividade_ambas.id) or \
                   (selected_tipo_atividade_id == tipo_atividade_ambas.id and e.tipo_atividade_id != tipo_atividade_ambas.id):
                    afinidade['tipo_atividade'] = 2.5

        # Tipo Participação: 5% se igual, 2.5% se compatibilidade parcial
        if selected_tipo_participacao_id and e.tipo_participacao_id == selected_tipo_participacao_id:
            afinidade['tipo_participacao'] = 5
        elif selected_tipo_participacao_id:
            tipo_participacao_ambos = TipoParticipacao.query.filter_by(nome='Ambos').first()
            if tipo_participacao_ambos:
                if (e.tipo_participacao_id == tipo_participacao_ambos.id and selected_tipo_participacao_id != tipo_participacao_ambos.id) or \
                   (selected_tipo_participacao_id == tipo_participacao_ambos.id and e.tipo_participacao_id != tipo_participacao_ambos.id):
                    afinidade['tipo_participacao'] = 2.5

        afinidade['total'] = sum([afinidade[k] for k in ['atributos','curso','campus','categoria','tipo_atividade','tipo_participacao']])
        afinidade_resultados.append((e, afinidade))

    afinidade_resultados.sort(key=lambda x: x[1]['total'], reverse=True)
    recomendadas = [ (e, af) for e, af in afinidade_resultados if af['total'] > 0 ]

    return render_template('result.html',
                         entidades=recomendadas,
                         curso_nome=curso.nome_curso if curso else '',
                         periodo=periodo,
                         campus=campus.nome_campus if campus else '',
                         categoria=categoria_obj.nome if categoria_obj else '',
                         tipo_atividade=tipo_atividade_obj.nome if tipo_atividade_obj else '',
                         tipo_participacao=tipo_participacao_obj.nome if tipo_participacao_obj else '',
                         atributos_selecionados=atributos_selecionados)


@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        campus_id = request.form['campus_id']
        categoria_id = request.form['categoria_id']
        tipo_atividade_id = request.form['tipo_atividade_id']
        tipo_participacao_id = request.form['tipo_participacao_id']
        url_pagina = request.form['url_pagina']
        atributos_ids = request.form.getlist('atributos')
        cursos_ids = request.form.getlist('cursos')
        imagem_file = request.files.get('imagem')
        imagem_base64 = None
        if imagem_file and imagem_file.filename:
            imagem_bytes = imagem_file.read()
            imagem_base64 = base64.b64encode(imagem_bytes).decode('utf-8')
        nova_entidade = Entidade(
            nome=nome,
            campus_id=campus_id if campus_id != 'ambos' else None,
            categoria_id=categoria_id,
            tipo_atividade_id=tipo_atividade_id,
            tipo_participacao_id=tipo_participacao_id,
            url_pagina=url_pagina,
            imagem_base64=imagem_base64
        )
        if atributos_ids:
            nova_entidade.atributos = [Atributo.query.get(int(aid)) for aid in atributos_ids]
        if cursos_ids:
            nova_entidade.cursos = [Curso.query.get(cid) for cid in cursos_ids]
        db.session.add(nova_entidade)
        db.session.commit()
        flash('Entidade cadastrada com sucesso!', 'success')
        return redirect(url_for('index'))
    campus_list = Campus.query.order_by('nome_campus').all()
    categorias = Categoria.query.order_by('nome').all()
    tipos_atividade = TipoAtividade.query.order_by('nome').all()
    tipos_participacao = TipoParticipacao.query.order_by('nome').all()
    todos_atributos = Atributo.query.order_by('nome').all()
    todos_cursos = Curso.query.order_by('nome_curso').all()
    return render_template('cadastro.html', campus_list=campus_list, categorias=categorias,
                           tipos_atividade=tipos_atividade, tipos_participacao=tipos_participacao,
                           todos_atributos=todos_atributos, todos_cursos=todos_cursos)

@app.route('/entidades')
def entidades():
    todas_entidades = Entidade.query.order_by(Entidade.nome).all()
    entidades_completas = []
    for entidade in todas_entidades:
        categoria = Categoria.query.get(entidade.categoria_id)
        tipo_atividade = TipoAtividade.query.get(entidade.tipo_atividade_id)
        tipo_participacao = TipoParticipacao.query.get(entidade.tipo_participacao_id)
        cursos = [curso.nome_curso for curso in entidade.cursos]
        atributos = [atributo.nome for atributo in entidade.atributos]

        entidades_completas.append({
            'nome': entidade.nome,
            'campus': entidade.campus.nome_campus if entidade.campus else 'Ambos',
            'categoria': categoria.nome if categoria else '',
            'tipo_atividade': tipo_atividade.nome if tipo_atividade else '',
            'tipo_participacao': tipo_participacao.nome if tipo_participacao else '',
            'url_pagina': entidade.url_pagina,
            'imagem_base64': entidade.imagem_base64,
            'cursos': cursos,
            'atributos': atributos
        })
    return render_template('entidades.html', entidades=entidades_completas)

if __name__ == '__main__':
    app.run(debug=True)