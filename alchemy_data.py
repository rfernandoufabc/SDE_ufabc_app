import base64
from pathlib import Path


def load_entity_image(entity_var_name):
    try:
        image_path = Path(__file__).parent / 'static' / 'images' / 'entidades' / f"{entity_var_name}.png"
        if image_path.exists():
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                return encoded_string
        return None
    except Exception as e:
        print(f"Erro ao carregar imagem para {entity_var_name}: {e}")
        return None


def init_models(db):
    global Campus, Curso, Entidade, Atributo, entidade_curso, entidade_atributo, Categoria, TipoAtividade, TipoParticipacao

    entidade_curso = db.Table('entidade_curso',
                              db.Column('entidade_id', db.Integer, db.ForeignKey('entidade.id'), primary_key=True),
                              db.Column('curso_id', db.String(50), db.ForeignKey('curso.id_curso'), primary_key=True))

    entidade_atributo = db.Table('entidade_atributo',
                                 db.Column('entidade_id', db.Integer, db.ForeignKey('entidade.id'), primary_key=True),
                                 db.Column('atributo_id', db.Integer, db.ForeignKey('atributo.id'), primary_key=True))

    class Campus(db.Model):
        id = db.Column(db.String(3), primary_key=True)
        nome_campus = db.Column(db.String(50), nullable=False)
        cursos = db.relationship('Curso', backref='campus', lazy=True)
        entidades = db.relationship('Entidade', backref='campus', lazy=True)

        def __repr__(self):
            return f'<Campus {self.nome_campus}>'

    class Curso(db.Model):
        id_curso = db.Column(db.String(50), primary_key=True)
        nome_curso = db.Column(db.String(100), nullable=False)
        categoria = db.Column(db.String(30), nullable=False)
        campus_id = db.Column(db.String(3), db.ForeignKey('campus.id'), nullable=True)

        def __repr__(self):
            return f'<Curso {self.nome_curso}>'

    class Categoria(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(50), unique=True, nullable=False)
        entidades = db.relationship('Entidade', backref='categoria_ref', lazy=True)

        def __repr__(self):
            return f'<Categoria {self.nome}>'

    class TipoAtividade(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(20), unique=True, nullable=False)
        entidades = db.relationship('Entidade', backref='tipo_atividade_ref', lazy=True)

        def __repr__(self):
            return f'<TipoAtividade {self.nome}>'

    class TipoParticipacao(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(20), unique=True, nullable=False)
        entidades = db.relationship('Entidade', backref='tipo_participacao_ref', lazy=True)

        def __repr__(self):
            return f'<TipoParticipacao {self.nome}>'

    class Entidade(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(100), nullable=False)
        campus_id = db.Column(db.String(3), db.ForeignKey('campus.id'), nullable=True)
        categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True)
        tipo_atividade_id = db.Column(db.Integer, db.ForeignKey('tipo_atividade.id'), nullable=True)
        tipo_participacao_id = db.Column(db.Integer, db.ForeignKey('tipo_participacao.id'), nullable=True)
        imagem_base64 = db.Column(db.Text, nullable=True)
        url_pagina = db.Column(db.String(200), nullable=True)
        atributos = db.relationship('Atributo', secondary='entidade_atributo', backref='entidades')
        cursos = db.relationship('Curso', secondary='entidade_curso', backref='entidades')

        def __repr__(self):
            return f'<Entidade {self.nome}>'

    class Atributo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(50), unique=True, nullable=False)

        def __repr__(self):
            return f'<Atributo {self.nome}>'

    return Campus, Curso, Entidade, Atributo, entidade_curso, entidade_atributo, Categoria, TipoAtividade, TipoParticipacao


CATEGORIAS = {
    'CAT_ACADEMICA': 'Acadêmica',
    'CAT_EMPRESARIAL': 'Empresarial',
    'CAT_COMPETICAO_TECNOLOGICA': 'Competição Tecnológica',
    'CAT_TECNOLOGICA': 'Tecnológica'
}

ATV_PRATICAS = 'ATV_PRAT'
ATV_TEORICAS = 'ATV_TEO'
ATV_AMBAS = 'ATV_AMB'

PART_GRUPO = 'PART_GRP'
PART_INDIVIDUAL = 'PART_IND'
PART_AMBOS = 'PART_AMB'

def init_db(app, db):
    with app.app_context():
        db.drop_all()

        db.create_all()

        db.session.commit()

        campus_sa = Campus(id='SA', nome_campus='Santo André')
        campus_sbc = Campus(id='SBC', nome_campus='São Bernardo do Campo')
        campus_amb = Campus(id='AMB', nome_campus='Ambos')

        db.session.add_all([campus_sa, campus_sbc, campus_amb])
        db.session.commit()

        curso_b_biotecnologia = Curso(id_curso='B_BIOTECNOLOGIA', nome_curso='Bacharelado em Biotecnologia',
                                      categoria='Bacharelados', campus_id='SA')
        curso_b_ciencia_computacao = Curso(id_curso='B_CIENCIA_COMPUTACAO',
                                           nome_curso='Bacharelado em Ciência da Computação', categoria='Bacharelados',
                                           campus_id='SA')
        curso_b_ciencia_dados = Curso(id_curso='B_CIENCIA_DADOS', nome_curso='Bacharelado em Ciência de Dados',
                                      categoria='Bacharelados', campus_id='SA')
        curso_b_ciencias_biologicas = Curso(id_curso='B_CIENCIAS_BIOLOGICAS',
                                            nome_curso='Bacharelado em Ciências Biológicas', categoria='Bacharelados',
                                            campus_id='SA')
        curso_b_ciencias_economicas = Curso(id_curso='B_CIENCIAS_ECONOMICAS',
                                            nome_curso='Bacharelado em Ciências Econômicas', categoria='Bacharelados',
                                            campus_id='SBC')
        curso_b_filosofia = Curso(id_curso='B_FILOSOFIA', nome_curso='Bacharelado em Filosofia',
                                  categoria='Bacharelados', campus_id='SBC')
        curso_b_fisica = Curso(id_curso='B_FISICA', nome_curso='Bacharelado em Física', categoria='Bacharelados',
                               campus_id='SA')
        curso_b_matematica = Curso(id_curso='B_MATEMATICA', nome_curso='Bacharelado em Matemática',
                                   categoria='Bacharelados', campus_id='SA')
        curso_b_neurociencia = Curso(id_curso='B_NEUROCIENCIA', nome_curso='Bacharelado em Neurociência',
                                     categoria='Bacharelados', campus_id='SBC')
        curso_b_planejamento_territorial = Curso(id_curso='B_PLANEJAMENTO_TERRITORIAL',
                                                 nome_curso='Bacharelado em Planejamento Territorial',
                                                 categoria='Bacharelados', campus_id='SBC')
        curso_b_politicas_publicas = Curso(id_curso='B_POLITICAS_PUBLICAS',
                                           nome_curso='Bacharelado em Políticas Públicas', categoria='Bacharelados',
                                           campus_id='SBC')
        curso_b_quimica = Curso(id_curso='B_QUIMICA', nome_curso='Bacharelado em Química', categoria='Bacharelados',
                                campus_id='SA')
        curso_b_relacoes_internacionais = Curso(id_curso='B_RELACOES_INTERNACIONAIS',
                                                nome_curso='Bacharelado em Relações Internacionais',
                                                categoria='Bacharelados', campus_id='SBC')
        curso_b_ciencia_tecnologia = Curso(id_curso='B_CIENCIA_TECNOLOGIA',
                                           nome_curso='Bacharelado em Ciência e Tecnologia (BC&T)',
                                           categoria='Cursos de Ingresso', campus_id='AMB')
        curso_b_ciencias_humanidades = Curso(id_curso='B_CIENCIAS_HUMANIDADES',
                                             nome_curso='Bacharelado em Ciências e Humanidades (BC&H)',
                                             categoria='Cursos de Ingresso', campus_id='SBC')
        curso_e_aeroespacial = Curso(id_curso='E_AEROESPACIAL', nome_curso='Engenharia Aeroespacial',
                                     categoria='Engenharias', campus_id='SBC')
        curso_e_ambiental_urbana = Curso(id_curso='E_AMBIENTAL_URBANA', nome_curso='Engenharia Ambiental e Urbana',
                                         categoria='Engenharias', campus_id='SA')
        curso_e_biomedica = Curso(id_curso='E_BIOMEDICA', nome_curso='Engenharia Biomédica', categoria='Engenharias',
                                  campus_id='SBC')
        curso_e_energia = Curso(id_curso='E_ENERGIA', nome_curso='Engenharia de Energia', categoria='Engenharias',
                                campus_id='SA')
        curso_e_gestao = Curso(id_curso='E_GESTAO', nome_curso='Engenharia de Gestão', categoria='Engenharias',
                               campus_id='SBC')
        curso_e_informacao = Curso(id_curso='E_INFORMACAO', nome_curso='Engenharia de Informação',
                                   categoria='Engenharias', campus_id='SA')
        curso_e_instrumentacao_automacao_robotica = Curso(id_curso='E_INSTRUMENTACAO_AUTOMACAO_ROBOTICA',
                                                          nome_curso='Engenharia de Instrumentação, Automação e Robótica',
                                                          categoria='Engenharias', campus_id='SA')
        curso_e_materiais = Curso(id_curso='E_MATERIAIS', nome_curso='Engenharia de Materiais', categoria='Engenharias',
                                  campus_id='SA')
        curso_l_ciencias_biologicas = Curso(id_curso='L_CIENCIAS_BIOLOGICAS',
                                            nome_curso='Licenciatura em Ciências Biológicas', categoria='Licenciaturas',
                                            campus_id='SA')
        curso_l_filosofia = Curso(id_curso='L_FILOSOFIA', nome_curso='Licenciatura em Filosofia',
                                  categoria='Licenciaturas', campus_id='SBC')
        curso_l_fisica = Curso(id_curso='L_FISICA', nome_curso='Licenciatura em Física', categoria='Licenciaturas',
                               campus_id='SA')
        curso_l_historia = Curso(id_curso='L_HISTORIA', nome_curso='Licenciatura em História',
                                 categoria='Licenciaturas', campus_id='SBC')
        curso_l_matematica = Curso(id_curso='L_MATEMATICA', nome_curso='Licenciatura em Matemática',
                                   categoria='Licenciaturas', campus_id='SA')
        curso_l_quimica = Curso(id_curso='L_QUIMICA', nome_curso='Licenciatura em Química', categoria='Licenciaturas',
                                campus_id='SA')
        curso_l_ciencias_humanas = Curso(id_curso='L_CIENCIAS_HUMANAS',
                                         nome_curso='Licenciatura em Ciências Humanas (LCH)',
                                         categoria='Cursos de Ingresso', campus_id='SBC')
        curso_l_ciencias_naturais_exatas = Curso(id_curso='L_CIENCIAS_NATURAIS_EXATAS',
                                                 nome_curso='Licenciatura em Ciências Naturais e Exatas (LCNE)',
                                                 categoria='Cursos de Ingresso', campus_id='SA')

        db.session.add_all([
            curso_b_biotecnologia,
            curso_b_ciencia_computacao,
            curso_b_ciencia_dados,
            curso_b_ciencias_biologicas,
            curso_b_ciencias_economicas,
            curso_b_filosofia,
            curso_b_fisica,
            curso_b_matematica,
            curso_b_neurociencia,
            curso_b_planejamento_territorial,
            curso_b_politicas_publicas,
            curso_b_quimica,
            curso_b_relacoes_internacionais,
            curso_b_ciencia_tecnologia,
            curso_b_ciencias_humanidades,
            curso_e_aeroespacial,
            curso_e_ambiental_urbana,
            curso_e_biomedica,
            curso_e_energia,
            curso_e_gestao,
            curso_e_informacao,
            curso_e_instrumentacao_automacao_robotica,
            curso_e_materiais,
            curso_l_ciencias_biologicas,
            curso_l_filosofia,
            curso_l_fisica,
            curso_l_historia,
            curso_l_matematica,
            curso_l_quimica,
            curso_l_ciencias_humanas,
            curso_l_ciencias_naturais_exatas
        ])
        db.session.commit()

        aerodinamica = Atributo(id=1, nome='Aerodinâmica')

        arte = Atributo(id=2, nome='Arte')

        astronomia = Atributo(id=3, nome='Astronomia')

        automobilismo = Atributo(id=4, nome='Automobilismo')

        blockchain_atrb = Atributo(id=5, nome='Blockchain')

        carreira = Atributo(id=6, nome='Carreira')

        ciencia = Atributo(id=7, nome='Ciência')

        colaboracao = Atributo(id=8, nome='Colaboração')

        competicao = Atributo(id=9, nome='Competição')

        comunicacao = Atributo(id=10, nome='Comunicação')

        consultoria = Atributo(id=11, nome='Consultoria')

        criptomoeda = Atributo(id=12, nome='Criptomoeda')

        cultura = Atributo(id=13, nome='Cultura')

        dados = Atributo(id=14, nome='Dados')

        danca = Atributo(id=15, nome='Dança')

        debate = Atributo(id=16, nome='Debate')

        desafios = Atributo(id=17, nome='Desafios')

        desenvolvimento_pessoal = Atributo(id=18, nome='Desenvolvimento pessoal')

        diplomacia = Atributo(id=19, nome='Diplomacia')

        divulgacao_cientifica = Atributo(id=20, nome='Divulgação científica')

        empreendedorismo = Atributo(id=21, nome='Empreendedorismo')

        empresa_junior = Atributo(id=22, nome='Empresa júnior')

        engenharia = Atributo(id=23, nome='Engenharia')

        espaco = Atributo(id=24, nome='Espaço')

        esporte = Atributo(id=25, nome='Esporte')

        feminismo = Atributo(id=26, nome='Feminismo')

        foguetes = Atributo(id=27, nome='Foguetes')

        fotografia = Atributo(id=28, nome='Fotografia')

        futuro = Atributo(id=29, nome='Futuro')

        gestao = Atributo(id=30, nome='Gestão')

        gestao_ambiental = Atributo(id=31, nome='Gestão ambiental')

        historia = Atributo(id=32, nome='História')

        inovacao = Atributo(id=33, nome='Inovação')

        inteligencia_artificial = Atributo(id=34, nome='Inteligência artificial')

        internacional = Atributo(id=35, nome='Internacional')

        lideranca = Atributo(id=36, nome='Liderança')

        mecanica = Atributo(id=37, nome='Mecânica')

        meio_ambiente = Atributo(id=38, nome='Meio ambiente')

        musica = Atributo(id=39, nome='Música')

        negocios = Atributo(id=40, nome='Negócios')

        observacao = Atributo(id=41, nome='Observação')

        pesquisa = Atributo(id=42, nome='Pesquisa')

        politica = Atributo(id=43, nome='Política')

        programacao = Atributo(id=44, nome='Programação')

        projeto = Atributo(id=45, nome='Projeto')

        projetos = Atributo(id=46, nome='Projetos')

        pratica = Atributo(id=47, nome='Prática')

        robotica = Atributo(id=48, nome='Robotica')

        seguranca_digital = Atributo(id=49, nome='Segurança digital')

        startup = Atributo(id=50, nome='Startup')

        sustentabilidade = Atributo(id=51, nome='Sustentabilidade')

        tecnologia = Atributo(id=52, nome='Tecnologia')

        telescopio = Atributo(id=53, nome='Telescópio')

        voluntariado = Atributo(id=54, nome='Voluntariado')

        db.session.add_all([
            aerodinamica,
            arte,
            astronomia,
            automobilismo,
            blockchain_atrb,
            carreira,
            ciencia,
            colaboracao,
            competicao,
            comunicacao,
            consultoria,
            criptomoeda,
            cultura,
            dados,
            danca,
            debate,
            desafios,
            desenvolvimento_pessoal,
            diplomacia,
            divulgacao_cientifica,
            empreendedorismo,
            empresa_junior,
            engenharia,
            espaco,
            esporte,
            feminismo,
            foguetes,
            fotografia,
            futuro,
            gestao,
            gestao_ambiental,
            historia,
            inovacao,
            inteligencia_artificial,
            internacional,
            lideranca,
            mecanica,
            meio_ambiente,
            musica,
            negocios,
            observacao,
            pesquisa,
            politica,
            programacao,
            projeto,
            projetos,
            pratica,
            robotica,
            seguranca_digital,
            startup,
            sustentabilidade,
            tecnologia,
            telescopio,
            voluntariado])

        categorias_objs = [
            Categoria(nome='Acadêmica'),
            Categoria(nome='Empresarial'),
            Categoria(nome='Competição Tecnológica'),
            Categoria(nome='Tecnológica')
        ]
        db.session.add_all(categorias_objs)
        tipos_atividade_objs = [
            TipoAtividade(nome='Práticas'),
            TipoAtividade(nome='Teóricas'),
            TipoAtividade(nome='Ambas')
        ]
        db.session.add_all(tipos_atividade_objs)
        tipos_participacao_objs = [
            TipoParticipacao(nome='Grupo'),
            TipoParticipacao(nome='Individual'),
            TipoParticipacao(nome='Ambos')
        ]
        db.session.add_all(tipos_participacao_objs)
        db.session.commit()

        cat_academica = Categoria.query.filter_by(nome='Acadêmica').first()
        cat_empresarial = Categoria.query.filter_by(nome='Empresarial').first()
        cat_competicao = Categoria.query.filter_by(nome='Competição Tecnológica').first()
        cat_tecnologica = Categoria.query.filter_by(nome='Tecnológica').first()
        tipo_ambas = TipoAtividade.query.filter_by(nome='Ambas').first()
        tipo_praticas = TipoAtividade.query.filter_by(nome='Práticas').first()
        tipo_teoricas = TipoAtividade.query.filter_by(nome='Teóricas').first()
        part_grupo = TipoParticipacao.query.filter_by(nome='Grupo').first()
        part_ambos = TipoParticipacao.query.filter_by(nome='Ambos').first()

        aiesec = Entidade(nome='AIESEC', campus_id='AS', categoria_id=cat_academica.id, tipo_atividade_id=tipo_ambas.id,
                          tipo_participacao_id=part_grupo.id, url_pagina='https://www.instagram.com/aiesecpelobrasil/')
        arcturus = Entidade(nome='Arcturus - Clube de Astronomia do ABC;', campus_id='AS',
                            categoria_id=cat_academica.id, tipo_atividade_id=tipo_ambas.id,
                            tipo_participacao_id=part_ambos.id, url_pagina='https://www.instagram.com/arcturusufabc/')
        abcjr = Entidade(nome='Associação ABC Jr.', campus_id='AS', categoria_id=cat_empresarial.id,
                         tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_ambos.id, url_pagina='https://www.instagram.com/ufabcjr/')
        baja = Entidade(nome='Baja UFABC', campus_id='AS', categoria_id=cat_competicao.id,
                        tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_grupo.id, url_pagina='https://www.instagram.com/bajaufabc')
        challenger = Entidade(nome='Challenger Electric Racing Team', campus_id='AS', categoria_id=cat_competicao.id,
                              tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_grupo.id, url_pagina='https://www.instagram.com/challenger_ufabc/')
        colibri = Entidade(nome='Colibri Helicopter Design', campus_id='SBC', categoria_id=cat_academica.id,
                           tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_grupo.id, url_pagina='https://www.facebook.com/colibriufabc')
        dojo = Entidade(nome='Dojo', campus_id='AS', categoria_id=cat_competicao.id, tipo_atividade_id=tipo_praticas.id,
                        tipo_participacao_id=part_grupo.id, url_pagina='https://www.facebook.com/ufabcdojo')
        enactus = Entidade(nome='Enactus', campus_id='AS', categoria_id=cat_academica.id,
                           tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_ambos.id, url_pagina='https://www.instagram.com/enactusufabc/')
        finance = Entidade(nome='Finance', campus_id='AS', categoria_id=cat_empresarial.id,
                           tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_ambos.id, url_pagina='https://www.instagram.com/ufabcfinance/')
        future_club = Entidade(nome='Future Club', campus_id='AS', categoria_id=cat_academica.id,
                               tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_ambos.id, url_pagina='https://www.facebook.com/FutureClubUFABC/')
        gpda = Entidade(nome='GPDA - Grupo de Pesquisa e Desenvolvimento Aeroespacial', campus_id='SBC',
                        categoria_id=cat_academica.id, tipo_atividade_id=tipo_praticas.id,
                        tipo_participacao_id=part_grupo.id, url_pagina='https://www.instagram.com/gpdaufabc/')
        harpia = Entidade(nome='Harpia Aerodesign', campus_id='SBC', categoria_id=cat_competicao.id,
                          tipo_atividade_id=tipo_praticas.id, tipo_participacao_id=part_grupo.id, url_pagina='https://www.instagram.com/harpiaaerodesign/')
        ieee = Entidade(nome='IEEE UFABC', campus_id='AS', categoria_id=cat_academica.id,
                        tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_ambos.id, url_pagina='https://www.instagram.com/ieeeufabc/')
        inseri = Entidade(nome='InseRI', campus_id='SBC', categoria_id=cat_academica.id,
                          tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_ambos.id, url_pagina='https://www.instagram.com/inseriufabc/')
        lizard = Entidade(nome='Lizard', campus_id='SBC', categoria_id=cat_competicao.id,
                          tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_grupo.id, url_pagina='https://www.instagram.com/lizard_ufabc/')
        nucleo_empreendedorismo = Entidade(nome='Núcleo de Empreendedorismo e Liberdade Econômica', campus_id='AS',
                                           categoria_id=cat_empresarial.id, tipo_atividade_id=tipo_ambas.id,
                                           tipo_participacao_id=part_grupo.id, url_pagina='https://www.instagram.com/neliebrasil/')
        osa = Entidade(nome='OSA - UFABC Student Chapter', campus_id='AS', categoria_id=cat_academica.id,
                       tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_grupo.id, url_pagina='https://www.facebook.com/OSAUFABCStudentChapter/')
        pacoca_devclub = Entidade(nome='Paçoca DevClub', campus_id='AS', categoria_id=cat_academica.id,
                                  tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_ambos.id, url_pagina='https://sites.google.com/view/pacocadevclub/in%C3%ADcio')
        rocket_design = Entidade(nome='Rocket Design', campus_id='SBC', categoria_id=cat_tecnologica.id,
                                 tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_grupo.id, url_pagina='https://www.instagram.com/ufabcrocketdesign/')
        sapiens = Entidade(nome='Sapiens - Vitrine da Neurociência', campus_id='SBC', categoria_id=cat_academica.id,
                           tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_ambos.id, url_pagina='https://www.instagram.com/svneuro/')
        scuderia = Entidade(nome='Scuderia', campus_id='AS', categoria_id=cat_competicao.id,
                            tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_grupo.id, url_pagina='https://www.instagram.com/scuderiaufabc/')
        seiva_jr = Entidade(nome='Seiva Jr.', campus_id='AS', categoria_id=cat_academica.id,
                            tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_grupo.id, url_pagina='https://www.instagram.com/seivajr/')
        sirius = Entidade(nome='Sirius', campus_id='AS', categoria_id=cat_academica.id,
                          tipo_atividade_id=tipo_praticas.id, tipo_participacao_id=part_grupo.id, url_pagina='https://www.instagram.com/sirius.ufabc/')
        tamandutech = Entidade(nome='TamanduTech', campus_id='AS', categoria_id=cat_competicao.id,
                               tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_grupo.id, url_pagina='https://www.instagram.com/tamandutech/')
        ufabc_consulting_club = Entidade(nome='UFABC Consulting Club ', campus_id='AS', categoria_id=cat_empresarial.id,
                                         tipo_atividade_id=tipo_ambas.id, tipo_participacao_id=part_ambos.id, url_pagina='https://www.instagram.com/consultingclubufabc/')

        db.session.add_all([
            aiesec,
            abcjr,
            arcturus,
            baja,
            challenger,
            colibri,
            dojo,
            enactus,
            finance,
            future_club,
            gpda,
            harpia,
            ieee,
            inseri,
            lizard,
            nucleo_empreendedorismo,
            osa,
            pacoca_devclub,
            rocket_design,
            sapiens,
            scuderia,
            seiva_jr,
            sirius,
            tamandutech,
            ufabc_consulting_club
        ])
        db.session.commit()

        aiesec.atributos.append(lideranca)
        aiesec.atributos.append(voluntariado)
        aiesec.atributos.append(internacional)
        aiesec.atributos.append(gestao)
        aiesec.atributos.append(desenvolvimento_pessoal)
        arcturus.atributos.append(astronomia)
        arcturus.atributos.append(ciencia)
        arcturus.atributos.append(telescopio)
        arcturus.atributos.append(observacao)
        arcturus.atributos.append(espaco)
        abcjr.atributos.append(consultoria)
        abcjr.atributos.append(negocios)
        abcjr.atributos.append(empreendedorismo)
        abcjr.atributos.append(gestao)
        abcjr.atributos.append(empresa_junior)
        baja.atributos.append(engenharia)
        baja.atributos.append(automobilismo)
        baja.atributos.append(competicao)
        baja.atributos.append(projeto)
        baja.atributos.append(mecanica)
        challenger.atributos.append(debate)
        challenger.atributos.append(robotica)
        challenger.atributos.append(pesquisa)
        challenger.atributos.append(cultura)
        challenger.atributos.append(negocios)
        colibri.atributos.append(projeto)
        colibri.atributos.append(empreendedorismo)
        colibri.atributos.append(debate)
        colibri.atributos.append(diplomacia)
        colibri.atributos.append(lideranca)
        dojo.atributos.append(programacao)
        dojo.atributos.append(pratica)
        dojo.atributos.append(desafios)
        dojo.atributos.append(tecnologia)
        dojo.atributos.append(colaboracao)
        enactus.atributos.append(projeto)
        enactus.atributos.append(sustentabilidade)
        enactus.atributos.append(danca)
        enactus.atributos.append(inovacao)
        enactus.atributos.append(voluntariado)
        finance.atributos.append(cultura)
        finance.atributos.append(projeto)
        finance.atributos.append(ciencia)
        finance.atributos.append(fotografia)
        finance.atributos.append(arte)
        future_club.atributos.append(futuro)
        future_club.atributos.append(inovacao)
        future_club.atributos.append(tecnologia)
        future_club.atributos.append(empreendedorismo)
        future_club.atributos.append(carreira)
        gpda.atributos.append(projeto)
        gpda.atributos.append(historia)
        gpda.atributos.append(startup)
        gpda.atributos.append(inovacao)
        gpda.atributos.append(dados)
        harpia.atributos.append(projeto)
        harpia.atributos.append(startup)
        harpia.atributos.append(pesquisa)
        harpia.atributos.append(esporte)
        harpia.atributos.append(ciencia)
        ieee.atributos.append(inovacao)
        ieee.atributos.append(esporte)
        ieee.atributos.append(comunicacao)
        ieee.atributos.append(pesquisa)
        ieee.atributos.append(fotografia)
        inseri.atributos.append(ciencia)
        inseri.atributos.append(esporte)
        inseri.atributos.append(diplomacia)
        inseri.atributos.append(danca)
        inseri.atributos.append(historia)
        lizard.atributos.append(meio_ambiente)
        lizard.atributos.append(dados)
        lizard.atributos.append(startup)
        lizard.atributos.append(sustentabilidade)
        lizard.atributos.append(programacao)
        nucleo_empreendedorismo.atributos.append(fotografia)
        nucleo_empreendedorismo.atributos.append(inteligencia_artificial)
        nucleo_empreendedorismo.atributos.append(meio_ambiente)
        nucleo_empreendedorismo.atributos.append(robotica)
        nucleo_empreendedorismo.atributos.append(politica)
        osa.atributos.append(comunicacao)
        osa.atributos.append(inovacao)
        osa.atributos.append(ciencia)
        osa.atributos.append(musica)
        osa.atributos.append(cultura)
        pacoca_devclub.atributos.append(inovacao)
        pacoca_devclub.atributos.append(meio_ambiente)
        pacoca_devclub.atributos.append(debate)
        pacoca_devclub.atributos.append(startup)
        pacoca_devclub.atributos.append(sustentabilidade)
        rocket_design.atributos.append(engenharia)
        rocket_design.atributos.append(foguetes)
        rocket_design.atributos.append(aerodinamica)
        rocket_design.atributos.append(projeto)
        rocket_design.atributos.append(competicao)
        sapiens.atributos.append(inteligencia_artificial)
        sapiens.atributos.append(inovacao)
        sapiens.atributos.append(debate)
        sapiens.atributos.append(empreendedorismo)
        sapiens.atributos.append(pesquisa)
        scuderia.atributos.append(sustentabilidade)
        scuderia.atributos.append(inteligencia_artificial)
        scuderia.atributos.append(musica)
        scuderia.atributos.append(lideranca)
        scuderia.atributos.append(startup)
        seiva_jr.atributos.append(meio_ambiente)
        seiva_jr.atributos.append(consultoria)
        seiva_jr.atributos.append(sustentabilidade)
        seiva_jr.atributos.append(projetos)
        seiva_jr.atributos.append(gestao_ambiental)
        sirius.atributos.append(sustentabilidade)
        sirius.atributos.append(feminismo)
        sirius.atributos.append(esporte)
        sirius.atributos.append(programacao)
        sirius.atributos.append(pesquisa)
        tamandutech.atributos.append(projeto)
        tamandutech.atributos.append(negocios)
        tamandutech.atributos.append(empreendedorismo)
        tamandutech.atributos.append(programacao)
        tamandutech.atributos.append(meio_ambiente)
        ufabc_consulting_club.atributos.append(startup)
        ufabc_consulting_club.atributos.append(tecnologia)
        ufabc_consulting_club.atributos.append(ciencia)
        ufabc_consulting_club.atributos.append(inovacao)
        ufabc_consulting_club.atributos.append(meio_ambiente)

        def add_curso(entidade, curso):
            if curso:
                entidade.cursos.append(curso)

        # AIESEC - cursos de gestão e relações internacionais
        add_curso(aiesec, curso_e_gestao)
        add_curso(aiesec, curso_b_relacoes_internacionais)

        # ABC Jr - todos os cursos (empresa júnior multidisciplinar)
        add_curso(abcjr, curso_b_ciencia_tecnologia)
        add_curso(abcjr, curso_b_ciencias_humanidades)

        # Arcturus - cursos relacionados a física e engenharia
        add_curso(arcturus, curso_b_fisica)
        add_curso(arcturus, curso_l_fisica)
        add_curso(arcturus, curso_e_aeroespacial)

        # Baja - engenharias
        add_curso(baja, curso_b_ciencia_tecnologia)
        add_curso(baja, curso_e_materiais)
        add_curso(baja, curso_e_instrumentacao_automacao_robotica)

        # Challenger - engenharias
        add_curso(challenger, curso_b_ciencia_tecnologia)
        add_curso(challenger, curso_e_energia)
        add_curso(challenger, curso_e_instrumentacao_automacao_robotica)

        # Colibri - engenharias aeroespaciais
        add_curso(colibri, curso_e_aeroespacial)
        add_curso(colibri, curso_b_ciencia_tecnologia)

        # Dojo - computação e tecnologia
        add_curso(dojo, curso_b_ciencia_computacao)
        add_curso(dojo, curso_e_informacao)
        add_curso(dojo, curso_b_ciencia_tecnologia)

        # Finance - economia e gestão
        add_curso(finance, curso_b_ciencias_economicas)
        add_curso(finance, curso_e_gestao)
        add_curso(finance, curso_b_ciencias_humanidades)

        # Future Club - tecnologia e inovação
        add_curso(future_club, curso_b_ciencia_computacao)
        add_curso(future_club, curso_e_informacao)
        add_curso(future_club, curso_b_ciencia_tecnologia)

        # GPDA - engenharia aeroespacial
        add_curso(gpda, curso_e_aeroespacial)
        add_curso(gpda, curso_b_ciencia_tecnologia)

        # Harpia - engenharia aeroespacial
        add_curso(harpia, curso_e_aeroespacial)
        add_curso(harpia, curso_b_ciencia_tecnologia)

        # IEEE - engenharia e computação
        add_curso(ieee, curso_b_ciencia_computacao)
        add_curso(ieee, curso_e_informacao)
        add_curso(ieee, curso_b_ciencia_tecnologia)

        # InseRI - relações internacionais
        add_curso(inseri, curso_b_relacoes_internacionais)
        add_curso(inseri, curso_b_ciencias_humanidades)

        # Lizard - engenharia e sustentabilidade
        add_curso(lizard, curso_e_ambiental_urbana)
        add_curso(lizard, curso_b_ciencia_tecnologia)

        # Núcleo de Empreendedorismo - economia e gestão
        add_curso(nucleo_empreendedorismo, curso_b_ciencias_economicas)
        add_curso(nucleo_empreendedorismo, curso_e_gestao)

        # OSA - física e engenharia
        add_curso(osa, curso_b_fisica)
        add_curso(osa, curso_l_fisica)
        add_curso(osa, curso_b_ciencia_tecnologia)

        # Paçoca DevClub - computação e tecnologia
        add_curso(pacoca_devclub, curso_b_ciencia_computacao)
        add_curso(pacoca_devclub, curso_e_informacao)

        # Rocket Design - engenharia aeroespacial
        add_curso(rocket_design, curso_e_aeroespacial)
        add_curso(rocket_design, curso_b_ciencia_tecnologia)

        # Sapiens - neurociência
        add_curso(sapiens, curso_b_neurociencia)
        add_curso(sapiens, curso_b_ciencias_biologicas)

        # Scuderia - engenharias
        add_curso(scuderia, curso_b_ciencia_tecnologia)
        add_curso(scuderia, curso_e_instrumentacao_automacao_robotica)

        # Seiva Jr. - gestão ambiental
        add_curso(seiva_jr, curso_e_ambiental_urbana)
        add_curso(seiva_jr, curso_b_ciencia_tecnologia)

        # Sirius - engenharia aeroespacial e física
        add_curso(sirius, curso_e_aeroespacial)
        add_curso(sirius, curso_b_fisica)

        # TamanduTech - robótica e automação
        add_curso(tamandutech, curso_e_instrumentacao_automacao_robotica)
        add_curso(tamandutech, curso_b_ciencia_tecnologia)

        # UFABC Consulting Club - gestão e economia
        add_curso(ufabc_consulting_club, curso_b_ciencias_economicas)
        add_curso(ufabc_consulting_club, curso_e_gestao)

        entidades_vars = [
            (aiesec, 'aiesec'),
            (arcturus, 'arcturus'),
            (abcjr, 'abcjr'),
            (baja, 'baja'),
            (challenger, 'challenger'),
            (colibri, 'colibri'),
            (dojo, 'dojo'),
            (enactus, 'enactus'),
            (finance, 'finance'),
            (future_club, 'future_club'),
            (gpda, 'gpda'),
            (harpia, 'harpia'),
            (ieee, 'ieee'),
            (inseri, 'inseri'),
            (lizard, 'lizard'),
            (nucleo_empreendedorismo, 'nucleo_empreendedorismo'),
            (osa, 'osa'),
            (pacoca_devclub, 'pacoca_devclub'),
            (rocket_design, 'rocket_design'),
            (sapiens, 'sapiens'),
            (scuderia, 'scuderia'),
            (seiva_jr, 'seiva_jr'),
            (sirius, 'sirius'),
            (tamandutech, 'tamandutech'),
            (ufabc_consulting_club, 'ufabc_consulting_club')
        ]

        for entidade, var_name in entidades_vars:
            imagem_base64 = load_entity_image(var_name)
            if imagem_base64:
                entidade.imagem_base64 = imagem_base64

        db.session.commit()
        print('Banco de dados inicializado com sucesso!')
