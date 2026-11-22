# Kill Mice · datos canónicos de personajes, enemigos, objetos y tablas.
# Única fuente para el PDF (tools/libro.py) y para el módulo de Foundry (tools/foundry.py).
# Inventario: 6 casillas (2 patas, 2 cuerpo, 2 mochila). Ranuras: pata (hábil), torpe, c1, c2, m1, m2.

# ---------------------------------------------------------------- objetos
# tipo: weapon | armor | item. ic = celda de una hoja de iconos (hoja, índice 1-9).
# fuego: arma de fuego (dado de munición tras cada gran pelea). mas: Masillas extra abatidos por golpe contra la Turba.
OBJ = {
 # armas cuerpo a cuerpo
 'kungfu': dict(n='Kung-fu ratonil', tipo='weapon', dmg='d6', ic=None, d='Garra, patada y proyección. Todos pueden hacerlo, sin arma.'),
 'katana': dict(n='Katana «Hattori Ratzo»', tipo='weapon', dmg='d8', dmg2='d10', ic=('armas', 1), d='Hoja de bisturí quirúrgico templada al mechero Bunsen, guarda de arandela de latón y empuñadura de hilo dental negro. d8 a una pata, d10 a dos. Corta cuerdas y bambú al instante.'),
 'nunchakus': dict(n='Nunchakus de eslabones de reloj', tipo='weapon', dmg='d6', mas=1, ic=('armas', 2), d='Dos tubos de correa de reloj unidos por eslabones. Abate un Masilla más por golpe contra la Turba.'),
 'bate': dict(n='Bate de palillo con clavos', tipo='weapon', dmg='d10', ic=('armas', 3), d='Palillo chino macizo tachonado con clavos de tapicería. d10 en las patas de El Martillo (Fuerte como un buey).'),
 'estrellas': dict(n='Estrellas de arandela dentada', tipo='weapon', dmg='d6', ic=('armas', 4), d='Arandelas limadas en estrella. d6 a distancia. No gastan usos contra Masillas.'),
 'horquilla': dict(n='Horquilla de plata y velo rojo', tipo='weapon', dmg='d6', ic=('armas2', 3), d='Horquilla nupcial afilada. d6 cuerpo a cuerpo. Abre cerraduras y corta cuerdas de un tajo.'),
 # armas de fuego
 'chispero': dict(n='Chispero compacto «Detective»', tipo='weapon', dmg='d6', fuego=True, pips=3, ic=('armas', 5), d='Tubo de bolígrafo, chispero piezoeléctrico y perdigones. d6 a distancia.'),
 'pistola-pesada': dict(n='Pistola pesada de muelle «Beretta»', tipo='weapon', dmg='d8', fuego=True, pips=3, ic=('armas', 6), d='Muelle de mechero y cañón de estilográfica. d8 a distancia. Pareja gemela: con una en cada pata, 2d8 y te quedas el mayor.'),
 'pistola-pesada-izq': dict(n='Pistola pesada «Taurus» (izquierda)', tipo='weapon', dmg='d8', fuego=True, pips=3, ic=('armas', 6), d='La gemela de la pata torpe. Con las dos a la vez: 2d8 y el mayor, o la suma contra Masillas.'),
 'magnum': dict(n='Cañón de perno «Model 29»', tipo='weapon', dmg='d10', fuego=True, pips=3, ic=('armas', 7), d='El .44 cromado de La Placa Rota, su Arma Firma. d10 a distancia (d8 en otras patas).'),
 'revolver-corto': dict(n='Revólver corto «Rossi 515»', tipo='weapon', dmg='d6', fuego=True, pips=3, ic=('armas', 5), d='d6 a distancia; d8 +2 contra quien tenga el tic descubierto.'),
 'subfusil': dict(n='Subfusil de ráfaga «MP7 de muelle»', tipo='weapon', dmg='d8', fuego=True, pips=3, mas=2, ic=('armas', 8), d='Tubos de bolígrafo y muelles en cadena. d8 a distancia. Cada ráfaga abate dos Masillas más.'),
 'escopeta': dict(n='Escopeta de cartucho «Mossberg»', tipo='weapon', dmg='d8', fuego=True, pips=3, ic=('armas', 9), d='d8 a distancia. ¡KA-CHINK!: si gastas el movimiento en amartillarla gritándolo en la mesa, ese disparo hace d10 + 1.'),
 'rifle-aguja': dict(n='Rifle de aguja «Dragunov»', tipo='weapon', dmg='d10', fuego=True, pips=3, mas=1, w=1, h=2, ic=('armas2', 1), d='Cañón largo con mira de lente de cámara. d10 a larga distancia, a dos patas; ocupa dos casillas. Perfora: abate un Masilla más.'),
 'hierro-turno': dict(n='El hierro de turno (bolsa naranja)', tipo='weapon', dmg='d6', ic=('equipo', 9), d='Empieza cada pelea con el revólver de tambor (d6) y sube un hierro cada vez que dispara a un Enemigo con Nombre: d8, d8 + 1, d10 (+2 Masillas) y d12. Nunca se recarga.'),
 'colt-placa': dict(n='Placa de la Guardia y chispero de respaldo', tipo='weapon', dmg='d6', fuego=True, pips=3, ic=('equipo2', 8), d='d6 a distancia. La placa evita problemas con la Guardia al final del Acto I.'),
 'petardos': dict(n='Manojo de petardos de cerilla', tipo='item', ic=('armas2', 2), d='Una vez por acto: d10 a un Enemigo con Nombre o abatimiento automático de 1d6 + 2 Masillas. Lleva también estrellas de arandela (d6 a distancia, sin gastar usos contra Masillas).'),
 # armaduras
 'mono-amarillo': dict(n='Mono amarillo acolchado', tipo='armor', arm=1, ic=('equipo', 2), d='Cinta aislante y tela de globo. Armadura 1.'),
 'cinturon': dict(n='Cinturón de hebilla de chapa y muñequeras', tipo='armor', arm=1, ic=('equipo', 4), d='Armadura 1. Se pierde a 0 PG hasta el final de la pelea (Cuanto más grandes son).'),
 'cazadora': dict(n='Cazadora de cuero de guante', tipo='armor', arm=1, ic=('equipo', 5), d='Armadura 1 (2 con Desesperación del perdedor).'),
 'gabardina': dict(n='Gabardina noir forrada', tipo='armor', arm=1, ic=('equipo', 6), d='Armadura 1.'),
 'vestido-rojo': dict(n='Vestido de novia de seda reforzada', tipo='armor', arm=1, ic=('equipo2', 5), d='Rojo de verdad. Armadura 1.'),
 # equipo
 'llaves-moto': dict(n='Llaves de la moto RC amarilla', tipo='item', ic=('equipo2', 2), d='El «Mosquito Amarillo»: moto teledirigida con franjas negras, puenteada con alambre. Ventaja para perseguir o huir por los tejados.'),
 'gafas-clavo': dict(n='Gafas ahumadas y cigarrillo de clavo', tipo='item', ic=('equipo', 3), d='Ventaja en las tiradas sobre la política y los secretos de las tríadas.'),
 'llaves-chevy': dict(n='Llaves del «Impala 81»', tipo='item', ic=('equipo2', 9), d='Coche RC policial sin distintivos. Ventaja para seguir a un furgón.'),
 'linterna': dict(n='Linterna de mechero y ganzúas', tipo='item', ic=('equipo', 7), d='Ventaja en investigación, cerrajería e intrusión.'),
 'dosier-yan': dict(n='Dosier confidencial de la familia Yan', tipo='item', ic=('equipo', 8), d='Fotos, cuentas y un plano de la casa de los Yan. Dice que el Sobre Rojo «no lleva pepitas, sino una llave».'),
 'bolsa-naranja': dict(n='Bolsa naranja «llena de hierros»', tipo='item', ic=('equipo', 9), d='Seis armas artesanales en escalera. Con ella, Mecha Corta nunca tira por munición.'),
 'herramientas': dict(n='Herramientas de relojero y mechas rápidas', tipo='item', ic=('equipo2', 1), d='Ventaja para puentear pilas, abrir cerraduras con pólvora o sabotear trampas.'),
 'sobre-rojo': dict(n='El Sobre Rojo', tipo='item', ic=('equipo2', 3), d='Sobre ceremonial rojo con caracteres dorados. Dentro, la mitad del Medallón Llave Fénix-Dragón.'),
 'medallon': dict(n='Medio Medallón Fénix-Dragón', tipo='item', ic=('equipo2', 4), d='Medio disco de relojería de oro macizo. Unido a su otra mitad en la columna de La Casa de las Hojas Azules, abre la Cámara Negra.'),
 'moneda-fortuna': dict(n='Moneda de Fortuna', tipo='item', ic=('equipo2', 6), d='Se gana asestando el último golpe a un nombre compartido. Gástala cuando quieras para repetir una tirada propia o activar gratis una técnica.'),
 'botiquin': dict(n='Botiquín de la Guardia', tipo='item', pips=3, ic=('condiciones', 5), d='Tres usos. Cada uso cura d4 PG o quita Magullado.'),
}
# condiciones de Kill Mice
COND = {
 'sirena-roja': dict(n='Sirena Roja', ic=('condiciones', 1), d='Sed de venganza. Tus ataques contra cualquier nombre de tu Lista son mejorados (un escalón de dado más). Desventaja en VOL para retirarte, negociar o atacar a otro mientras un nombre de tu Lista siga en pie frente a ti.', quita='Tachar un nombre de tu Lista.'),
 'aturdido': dict(n='Aturdido (oídos pitando)', ic=('condiciones', 2), d='Te ha alcanzado un bramido, un petardo o una mesa. Desventaja en las salvaciones de DES (también en la Esquiva acrobática).', quita='Gastar una acción en sacudirte los cristales, o tachar un nombre de tu Lista.'),
 'magullado': dict(n='Magullado (banquete en ruinas)', ic=('condiciones', 3), d='Caíste a 0 PG en el banquete y te reanimaron los sanitarios. Ocupa una casilla de cuerpo. Desventaja en FUE.', quita='Un vendaje o un uso del botiquín antes de entrar en La Casa de las Hojas Azules.'),
}

# ---------------------------------------------------------------- enemigos con nombre (los de las Listas) y PNJ
# tipo: teniente (Acto I) · propio (n.º 1 exclusivo) · campeon (n.º 4) · jefe · aliado
PNJ = [
 dict(slug='sheng', n='«Jet-Set» Sheng', tipo='teniente', acto=1, apodo='El Poste Rojo', fue=12, des=12, vol=13, pg=6, arm=1, atq=[('Pistola pesada «Norinco M1911»', 'd8')],
  d='Ejecutor jefe de los Mares Dorados. Traje cruzado de seda color crema forrado de rojo, anillos de oro y una bolsa de pipas que no se acaba nunca.',
  esp=[('Lacayo ablativo', 'Mientras quede al menos un Masilla en pie, cuando Sheng vaya a perder PG por un ataque puede tirar de un Farolillo como escudo: Sheng no sufre daño y ese Masilla cae en su lugar. Una vez por asalto.'),
       ('Inspirar lealtad', 'Cuando Sheng cae a 0 PG, todos los demás Enemigos con Nombre en pie hacen al instante un ataque gratuito de represalia contra el PJ que elijan.')],
  voz='Grave y arrogante, escupiendo cáscaras de pipa.', frase='«¡Cortadles los bigotes y traedme a la novia con el sobre!»'),
 dict(slug='tonyma', n='Tony Ma', tipo='teniente', acto=1, apodo='El Teniente Leal', fue=10, des=12, vol=11, pg=5, arm=1, atq=[('Chispero compacto «Walther P-5»', 'd6')],
  d='El perro fiel de Sheng. Pelo corto en punta, corbata aflojada y un cañón que señala a quien tiene que morir primero.',
  esp=[('Órdenes a gritos', 'Mientras Tony Ma siga en pie, cada vez que la Turba hiere a un PJ (porque falló su Esquiva acrobática), el golpe hace +2 de daño.')],
  voz='Ladra órdenes cortas señalando con la pistola.', frase='«¡Rodeadlos por la mesa del té! ¡Que no respiren!»'),
 dict(slug='alas', n='«Alas» Chu', tipo='teniente', acto=1, apodo='El Ejecutor', fue=11, des=11, vol=10, pg=5, arm=0, atq=[('Chispero automático «Glock 18»', 'd8')], mesa=5,
  d='Camisa estampada abierta, risa nerviosa y dos chisperos automáticos que vacía desde lo alto de las mesas. Solo con cinco o seis jugadores.',
  esp=[('Ráfaga abierta', 'Elige en su turno: d8 a un solo PJ, o d6 a dos PJ que estén juntos.')],
  voz='Risa nerviosa entre ráfaga y ráfaga.', frase='«¡A ver quién corre más que el plomo!»'),
 dict(slug='leung', n='«Ochenta y Ocho» Leung', tipo='teniente', acto=1, apodo='Capitán de los Maníacos', fue=11, des=12, vol=10, pg=5, arm=1, atq=[('Katana corta de cúter y «Glock 18»', 'd8')], mesa=6,
  d='Antifaz negro lacado, corbata fina y una katana corta de hoja de cúter. Manda a los Maníacos cuando no está Bill. Solo con seis jugadores.',
  esp=[('Los 88 no dejan testigos', 'Si un PJ está atendiendo a un invitado herido o protegiendo a León, Leung le ataca a él antes que a nadie y con Ventaja.')],
  voz='Ajustándose el antifaz con dos dedos.', frase='«Los 88 no dejamos testigos en las bodas.»'),
 dict(slug='sofie', n='«Cuchilla» Sofie', tipo='propio', acto=1, apodo='La Cortadora', fue=9, des=12, vol=11, pg=4, arm=0, atq=[('Estilete de aguja', 'd6')], dueno='mamba',
  d='Abogada, chófer y verduga de Bill: traje gris perla, melena negra a lo garçon y las llaves del furgón negro. Aparece al final del Acto I, al volante.',
  esp=[('Canta', 'Si La Mamba la deja a 0 PG sin matarla, Sofie canta a gritos dónde está La Casa de las Hojas Azules.')],
  voz='Fría, con desprecio de bufete caro.', frase='«Mi cliente no recibe sin cita. Y tú no tienes cita.»'),
 dict(slug='johnnymo', n='Johnny Mo «El Contable»', tipo='propio', acto=1, apodo='El Contable', fue=10, des=12, vol=10, pg=4, arm=1, atq=[('Dos chisperos cortos', 'd6')], dueno='vibora',
  d='Gafas redondas, raya al lado y un ábaco de cuentas de cristal en el bolsillo del pecho. Dirige el flanco del estanque.',
  esp=[('Cuentas pendientes', 'Si el Víbora le habla antes de disparar, Johnny Mo duda: su primer ataque contra él tiene Desventaja.')],
  voz='Cuenta en voz baja mientras dispara.', frase='«Cuarenta y tres… cuarenta y cuatro… tú eres el cuarenta y cinco.»'),
 dict(slug='clavos', n='«Clavos» Chen', tipo='propio', acto=1, apodo='El Rompehuesos', fue=13, des=8, vol=9, pg=5, arm=1, atq=[('Llave inglesa con cadena', 'd8')], dueno='martillo',
  d='Nariz rota, camiseta sucia y tirantes. Destroza el Paseo de las Estatuas y reta a El Martillo a un duelo a puñetazos.',
  esp=[('Duelo de fuerza', 'Si El Martillo acepta el duelo cuerpo a cuerpo, ningún Masilla interviene entre los dos hasta que uno caiga.')],
  voz='Gruñidos y nudillos crujiendo.', frase='«Te solté en el río. Esta vez te dejo en el fondo.»'),
 dict(slug='lau', n='Sargento Corrupto Lau', tipo='propio', acto=1, apodo='«Doble Sobre»', fue=10, des=11, vol=10, pg=4, arm=1, atq=[('Revólver policial', 'd6')], dueno='placa',
  d='Uniforme de la Guardia, chaleco abierto y un sobre de Bill asomando del bolsillo. Llega al final del Acto I para encubrir la huida del furgón. Lleva la placa del compañero muerto de La Placa Rota.',
  esp=[('Galones', 'Mientras lleve el uniforme puesto, los guardias de la Unidad Anti-Tríadas le obedecen: si La Placa Rota no lo desenmascara, los agentes estorban a los PJ.')],
  voz='Sonrisa grasienta, voz de sindicato.', frase='«Tranquila, compañera. Aquí no ha pasado nada que no se arregle con un sobre.»'),
 dict(slug='elle', n='«Ojo de Serpiente» Elle', tipo='propio', acto=2, apodo='La Tuerta', fue=9, des=13, vol=12, pg=4, arm=1, atq=[('Aguja envenenada y carabina', 'd8')], dueno='ojo',
  d='Francotiradora y espía jefe de Bill. Parche blanco con una serpiente roja pintada y bata blanca sobre negro. Espera en el puente de entrada de La Casa.',
  esp=[('Aguja envenenada', 'Su primer ataque cuerpo a cuerpo deja al objetivo Aturdido si falla una salvación de FUE.')],
  voz='Silba bajito entre frase y frase.', frase='«Te dejé un ojo por pena. Hoy vengo a por el otro.»'),
 dict(slug='pei', n='«Pólvora» Pei', tipo='propio', acto=2, apodo='El Artificiero', fue=10, des=12, vol=10, pg=4, arm=0, atq=[('Tubos lanzacohetes de bengala', 'd8')], dueno='mecha',
  d='Gafas de soldador en la frente, mandil quemado lleno de bengalas y una cerilla encendida entre los dientes. Prepara las cajas de pirotecnia del vestíbulo.',
  esp=[('Herencia explosiva', 'Al caer a 0 PG, su mochila de pirotecnia le regala a Mecha Corta un uso extra de Granada salvaje.')],
  voz='Ríe con cada chispa.', frase='«Tus planos eran buenos, chaval. Mis cerillas, mejores.»'),
 dict(slug='bill', n='Bill «Mandíbula» Jang', tipo='jefe', acto=2, apodo='El Gran Jefe', fue=14, des=14, vol=15, pg=10, arm=2, atq=[('Katana maestra «Colmillo de Dragón» y dardos de fósforo', 'esp')],
  d='Líder supremo del Escuadrón Víbora del Loto Negro. Mandíbula inferior de acero y oro de relojería, abrigo imperial de escamas lacadas y una paciencia de maestro de té.',
  esp=[('Daño escalable', 'Cada ataque de Bill hace tanto como el mayor golpe que haya dado cualquier PJ en la sesión, +1 (aunque ese PJ ya no esté en pie). Mientras nadie haya pasado de 8 en un golpe, tira además 1d10 + 2 y aplica el mayor.'),
       ('Espalda contra la pared', 'Si le atacan dos o más personajes en la misma secuencia, hace dos ataques completos en su turno hasta que acabe esa secuencia.'),
       ('Resistencia de jefe', 'La primera vez que llega a 0 PG tira 1d6: con par, se limpia la sangre de la mandíbula y sigue en pie con 3 PG. No vale contra el Golpe de los Cinco Puntos.')],
  voz='Pausada, teatral y paternal, acariciando la hoja.', frase='«No os confundáis: no fuisteis traicionados… fuisteis despedidos.»'),
 dict(slug='oren', n='O-Ren «La Tigresa»', tipo='campeon', acto=2, apodo='Campeona felina', fue=12, des=14, vol=12, pg=7, arm=1, atq=[('Garras de bisturí y cadena con bola', 'd8')],
  d='Kimono de combate a rayas negras y naranjas y media máscara de tigre de porcelana. Acrobática, silenciosa, cruel.',
  esp=[('Gato copión', 'Cada vez que un PJ esquiva su ataque con una Esquiva acrobática, ella lee sus movimientos: Armadura 2 durante el siguiente asalto.'),
       ('Segundo aliento', 'Al empezar cada secuencia recupera 2 PG mientras siga por encima de 0.')],
  voz='Susurro gélido tras la porcelana.', frase='«A ver si vuestro acero corta tan bien como vuestra lengua.»'),
 dict(slug='budd', n='Budd «El Sapo»', tipo='campeon', acto=2, apodo='El Coloso del Trabuco', fue=14, des=9, vol=12, pg=8, arm=1, tam=2, atq=[('Trabuco de sal gorda y machete', 'd8')],
  d='Una rata de sumo con cazadora de piel de sapo, sombrero gastado y tabaco de mascar. El doble de grande que cualquier ratón.',
  esp=[('Bramido aturdidor', 'En su turno puede soltar una descarga de sal y aire comprimido contra un PJ: salvación de VOL; si la falla, queda Aturdido y sufre 1d4.'),
       ('Pellejo curtido', 'Al empezar cada secuencia recupera 2 PG mientras siga por encima de 0.')],
  voz='Ronca, cínica, masticando tabaco.', frase='«Esa espada vale mucho dinero… lástima que vayas a tragarte un puñado de sal gorda.»'),
 dict(slug='leon', n='León Yan', tipo='aliado', acto=1, apodo='El Novio', fue=8, des=10, vol=11, pg=4, arm=0, atq=[],
  d='Heredero del mayor imperio de radio y prensa ratonil. Esmoquin impecable, flor roja en la solapa y más miedo que valor, aunque lo intenta.',
  esp=[('Pegado a Rosa', 'No ataca salvo acorralado. Los dos primeros ataques que recibe tienen Desventaja al daño.')],
  voz='Educado incluso cuando grita.', frase='«¿Esto también estaba en el presupuesto del catering?»'),
]
MASILLAS = [
 dict(slug='farolillo', n='Farolillo Azul', acto=1, d='Masilla de los Mares Dorados: traje barato, camisa blanca, corbata estrecha, gafas de sol y chispero. Un punto de daño lo deja fuera de combate.', por_pj=3),
 dict(slug='maniaco', n='Maníaco de la Guardia Interior', acto=2, d='Masilla de los 88 Maníacos: esmoquin negro, antifaz de kendo, katana de cúter o tubo lanzachispas. Un punto de daño lo deja fuera de combate.', por_pj=2),
]

# ---------------------------------------------------------------- personajes jugadores
# op: opciones de técnica que el diálogo de ataque ofrece (las aplica el módulo de Foundry):
#   paso (+1 escalón) · plano (+N daño) · ventaja (2 dados, el mayor) · suma (2 dados sumados) · ignora (armadura ignorada)
#   mas (+N Masillas) · explota (explota también con máximo − N) · fija (dado fijo) · minimo (dado mínimo) · escalera (Bolsa llena de armas)
#   auto: viene marcada por defecto
PJ = [
 dict(slug='mamba', n='La Mamba Amarilla', color='#F5C518', arq='Artista marcial', lema='«Tu kung-fu es fuerte. Lástima que tu nombre esté en mi cuaderno.»',
  fue=11, des=15, vol=12, pg=6, pepitas=10,
  aspecto='Ratona ágil de mirada letal, con un mono amarillo intenso de franjas negras laterales (cinta aislante y tela de globo), zapatillas amarillas y una katana impecable a la espalda.',
  inv=dict(pata='katana', torpe='nunchakus', c1='lista', c2='mono-amarillo', m1='llaves-moto'),
  lista=['sofie', 'sheng', 'leung', 'oren', 'bill'],
  tec=[('Manos sin sombra', 'Tu katana y tus nunchakus ignoran 1 punto de la Armadura de cualquier Enemigo con Nombre.'),
       ('Torbellino de furia', 'En cuanto abatas a tu primer enemigo de la pelea con katana o nunchakus, tus ataques de artes marciales hacen d8 como mínimo hasta que acabe, y tienes Ventaja en la Esquiva acrobática contra la Turba.'),
       ('Dim Mak', 'Una vez por sesión, desde el segundo asalto de una pelea, a pata desnuda contra un Enemigo con Nombre: salvación de DES. Si la superas, un lugarteniente queda a 1 PG de caer; a Bill Jang le quitas 5 PG directos, sin armadura.')],
  op=[dict(id='sombra', n='Manos sin sombra (−1 Armadura del objetivo)', ignora=1, auto=True), dict(id='torbellino', n='Torbellino de furia (mínimo d8)', minimo='d8')],
  vinculo='Rosa Muk y tú os entrenasteis con el mismo maestro y formasteis parte del antiguo escuadrón antes de que Bill Jang ordenara arrasar vuestro dojo el día que decidiste retirarte. «Cuchilla» Sofie, tu n.º 1, te cortó los bigotes mientras estabas inconsciente en el suelo. Hoy has venido a la boda para que Rosa tenga el final feliz que a ti te robaron… y porque sabes que los perros de Bill no podrán resistirse a aparecer.',
  opina={'martillo': 'Confías ciegamente en su acero.', 'vibora': 'Respetas su frialdad profesional, aunque antes trabajara para las tríadas.', 'mecha': 'Crees que os va a volar los bigotes a todos con tanta pólvora.'}),
 dict(slug='vibora', n='El Víbora de Terciopelo', color='#2B2B2B', arq='Asesino', lema='«Cuarenta de ellos, uno de mí. Parece que la cosa está igualada.»',
  fue=10, des=15, vol=11, pg=5, pepitas=40,
  aspecto='Ratón impecable con traje negro de corte hongkonés, camisa blanca sin una arruga, gafas de sol redondas de cristal de reloj ahumado y dos pistolas desenfundadas a la vez.',
  inv=dict(pata='pistola-pesada', torpe='pistola-pesada-izq', c1='lista', c2='gafas-clavo', m1='rifle-aguja'),
  lista=['johnnymo', 'tonyma', 'sheng', 'oren', 'bill'],
  tec=[('A dos hierros', 'Con una pistola en cada pata contra el mismo objetivo tiras 2d8 y eliges el mayor. Contra Masillas, sumas los dos dados. Contra un Enemigo con Nombre también puedes sumarlos, pero su Armadura cuenta doble en ese disparo.'),
       ('Carnaval de carnicería', 'Siempre que dispares contra Masillas, abates dos más de los que marque tu dado.'),
       ('Derramamiento de sangre heroico', 'En el Acto II, cualquier golpe de Bill o de sus campeones que te quite 3 PG o más te quita 1 PG extra; a cambio, tus dados de daño explotan con el máximo y con el valor anterior (7 u 8 en d8).')],
  op=[dict(id='dos', n='A dos hierros (2d8, el mayor)', ventaja=True), dict(id='suma', n='A dos hierros sumando (Armadura doble)', suma=True),
      dict(id='carnaval', n='Carnaval de carnicería (+2 Masillas)', mas=2, auto=True), dict(id='sangre', n='Sangre heroica, Acto II (explota con 7 u 8)', explota=1)],
  vinculo='Trabajaste como asesino a sueldo para los Mares Dorados hasta que te ordenaron ejecutar a León Yan hace seis meses. Te negaste: la madre de León te salvó de las ratas del canal cuando eras un crío. Esa misma noche, Johnny Mo «El Contable», tu n.º 1, y Tony Ma, tu n.º 2, te acribillaron por la espalda y te tiraron al puerto. León te invitó en secreto a su boda para darte las gracias; tú has venido a devolverle el favor limpiando tu pasado con plomo.',
  opina={'placa': 'Te habría metido entre rejas hace un año, pero hoy disparáis hacia el mismo lado.', 'mamba': 'Admiras su técnica limpia.'}),
 dict(slug='martillo', n='El Martillo de Paso', color='#7A7A7A', arq='Grandullón', lema='«¿Se suponía que eso tenía que doler?»',
  fue=15, des=9, vol=11, pg=8, pepitas=15,
  aspecto='El ratón más grande de la mesa: pelaje gris oscuro lleno de costurones, camiseta blanca de tirantes, esmoquin con las mangas arrancadas, muñequeras de cuero, cadena al cinto y un bate de palillo al hombro.',
  inv=dict(pata='bate', torpe='escopeta', c1='lista', c2='cinturon'),
  lista=['clavos', 'alas', 'tonyma', 'budd', 'bill'],
  tec=[('Fuerte como un buey', 'Tus golpes cuerpo a cuerpo hacen un escalón más (d10 con tu bate). Ventaja en todas las salvaciones de FUE. Puedes levantar una moto RC, una estatua o una mesa del banquete y estamparla como arma improvisada de d10.'),
       ('Toma de establecimiento', 'Tu primer ataque cuerpo a cuerpo de cada pelea hace +2. Furia creciente: si sacas 1 o 2 en tu dado de daño cuerpo a cuerpo, tu siguiente golpe hace +2 acumulativo hasta que des uno demoledor.'),
       ('Cuanto más grandes son', 'Empiezas con 8 PG. A 0 PG tienes Ventaja en tu primera salvación de FUE para no caer; a cambio, pierdes la Armadura del cinturón hasta que acabe la pelea.')],
  op=[dict(id='establecimiento', n='Toma de establecimiento (+2, primer golpe)', plano=2), dict(id='furia', n='Furia creciente (+2 por cada golpe flojo)', plano=2),
      dict(id='kachink', n='¡KA-CHINK! (escopeta: d10 + 1)', fija='d10', plano=1)],
  vinculo='Eras el guardaespaldas jefe de los muelles y primo lejano de Rosa Muk. Cuando te negaste a dejar pasar un cargamento de veneno de los Mares Dorados, «Clavos» Chen, tu n.º 1, y Budd «El Sapo», tu n.º 4, te emboscaron entre seis, te rompieron las dos patas con una llave inglesa y te soldaron dentro de una lata de aceite que tiraron al río. Sobreviviste a puro diente. Hoy llevas el esmoquin con las mangas arrancadas porque eres el padrino de seguridad de tu prima.',
  opina={'mamba': 'La proteges como a una hermana pequeña, igual que a Rosa.', 'ojo': 'Demasiado lista para su propio bien, pero sabe dónde golpear.'}),
 dict(slug='placa', n='La Placa Rota', color='#3F6B3A', arq='Poli desmadrada', lema='«¡Quieto ahí, escoria! Te avisé de que no probaras tu suerte conmigo.»',
  fue=11, des=13, vol=12, pg=6, pepitas=20,
  aspecto='Inspectora de homicidios de paisano: cazadora de cuero negra sobre camiseta verde arrugada, placa de la Guardia al cinturón, cicatriz en la ceja y un revólver cromado descomunal.',
  inv=dict(pata='magnum', torpe='colt-placa', c1='lista', c2='cazadora', m1='llaves-chevy'),
  lista=['lau', 'sheng', 'alas', 'budd', 'bill'],
  tec=[('Arma firma y epigrama', 'Tu .44 hace d10. Si antes o después de disparar sueltas en la mesa un chascarrillo macarra de cine policíaco, +2 de daño contra un Enemigo con Nombre (+4 si ya ha perdido la mitad de sus PG).'),
       ('¡Alto ahí! y disparo limpio', 'Una vez por pelea, como interrupción, impides que un enemigo huya de la escena. Ventaja y +2 al daño cuando disparas a un villano que usa a un inocente de escudo o rehén.'),
       ('Desesperación del perdedor', 'Mientras tengas menos PG que el Enemigo con Nombre que te ataca, tu Armadura sube a 2.')],
  op=[dict(id='epigrama', n='Epigrama «¡Blam, blam!» (+2)', plano=2), dict(id='epigrama4', n='Epigrama contra un herido (+4)', plano=4),
      dict(id='rehen', n='Disparo limpio contra un rehenero (Ventaja, +2)', ventaja=True, plano=2)],
  vinculo='Rosa Muk fue tu compañera de academia antes de entrar en los Tigres Voladores. Hace cuatro meses tu compañero de patrulla descubrió quién financiaba a Bill Jang desde dentro de la comisaría: el Sargento Corrupto Lau, tu n.º 1, os vendió a «Jet-Set» Sheng, tu n.º 2, en un almacén del puerto. Tu compañero murió en tus brazos y a ti te suspendieron de empleo y sueldo por «conducta temeraria». Hoy Rosa te ha sentado en la mesa de honor aunque el comisario no quería verte ni en pintura.',
  opina={'vibora': 'Tiene antecedentes de tres páginas, pero hoy haces la vista gorda.', 'ojo': 'Te ha sacado de más de un apuro legal en tugurios de mala muerte.'}),
 dict(slug='ojo', n='La Ojo de Cristal', color='#5B3F7A', arq='Detective privada', lema='«Llevo toda la vida esperando que un payaso con traje entre en mi despacho y me suelte una mentira como esa.»',
  fue=9, des=13, vol=14, pg=6, pepitas=30,
  aspecto='Investigadora de cine negro: chaqueta oscura entallada, melena suelta, parche elegante con una estrellita de plata, linterna metálica en una pata y un revólver corto en la sobaquera.',
  inv=dict(pata='revolver-corto', torpe='linterna', c1='lista', c2='gabardina', m1='dosier-yan'),
  lista=['elle', 'leung', 'tonyma', 'oren', 'bill'],
  tec=[('Descubrir el tic', 'Si intercambias una pulla afilada con un Enemigo con Nombre al empezar la escena o durante su monólogo, le encuentras el punto débil: tus ataques contra él hacen +2 hasta el final de la aventura (y tu revólver, d8). Con una acción libre puedes provocarlo para que te ataque a ti y no a un aliado herido.'),
       ('Disparo desarmante', 'Contra un Enemigo con Nombre armado, haz 2 de daño menos (mínimo 1): suelta el arma y pierde su siguiente ataque mientras la recupera.'),
       ('Déjate de cuentos', 'Una vez por acto, cuando el grupo especule sobre una pista, un PNJ o una ruta, el DJ te dice si vuestra teoría es cierta o falsa, y el detalle que nadie más ha visto.')],
  op=[dict(id='tic', n='Tic descubierto (d8 y +2)', fija='d8', plano=2), dict(id='desarme', n='Disparo desarmante (−2, suelta el arma)', plano=-2)],
  vinculo='Trabajas para los abogados de la familia de León Yan. Hace un año seguiste demasiado de cerca el rastro del dinero sucio de Bill Jang: su francotiradora y espía jefe, «Ojo de Serpiente» Elle, tu n.º 1, y «Ochenta y Ocho» Leung, tu n.º 2, te tendieron una trampa en tu propio despacho, te dejaron tuerta y quemaron tus archivos. León te ha contratado en secreto para vigilar la entrega del Sobre Rojo durante el banquete.',
  opina={'mecha': 'Te divierte su entusiasmo suicida.', 'placa': 'Respetas su olfato callejero.', 'vibora': 'Oculta más de lo que dice, pero cumple sus contratos.'}),
 dict(slug='mecha', n='Mecha Corta', color='#E8731C', arq='Pirado de la pólvora', lema='«Técnicamente es ilegal e inseguro guardar algo así en una boda, pero… ¡mirad cómo silba!»',
  fue=10, des=14, vol=10, pg=5, pepitas=10,
  aspecto='Ratón joven y fibroso de sonrisa desquiciada, camiseta de tirantes tiznada, dos cananas cruzadas de petardos de cerilla y una bolsa de deporte naranja de la que asoman seis cañones distintos.',
  inv=dict(pata='hierro-turno', torpe='petardos', c1='lista', c2='bolsa-naranja', m1='herramientas'),
  lista=['pei', 'alas', 'leung', 'budd', 'bill'],
  tec=[('Bolsa llena de armas', 'Nunca recargas ni tiras por munición. Cada turno que atacas a un Enemigo con Nombre sacas un hierro más grande: revólver d6, pistola d8, «Desert Eagle» d8 + 1, escopeta casera d10 (+2 Masillas) y rifle cañón de hojalata d12, que se desmonta entre chispas al acabar la pelea.'),
       ('Reabastecimiento rápido', 'Una vez por pelea, cuando un aliado saque un 1 en su dado de daño o se le encasquille el arma, le lanzas una pistola gritando «¡Coge esta!»: repite el ataque con +2.'),
       ('Granada salvaje', 'Una vez por acto, un petardo barre 1d6 + 2 Masillas o hace d10 a un Enemigo con Nombre. Si quieres, sin esquiva posible: tú te chamuscas 1 PG y alcanzas a otro enemigo cercano. Por mucho que te cacheen, siempre te queda una pistolita en el tobillo.')],
  op=[dict(id='escalera', n='Bolsa llena de armas (sube el hierro)', escalera=True, auto=True)],
  vinculo='Te encargaron los fuegos artificiales de la boda: eres amigo de la infancia del hermano pequeño de Rosa. Hace un año, el jefe pirotécnico de los Mares Dorados, «Pólvora» Pei, tu n.º 1, y «Alas» Chu, tu n.º 2, robaron tus diseños, volaron tu taller contigo dentro y lo vendieron como un accidente. Has venido con los petardos nupciales… y con la bolsa naranja cargada hasta las costuras.',
  opina={'vibora': 'Lo idolatras en secreto.', 'mamba': '«¡Tío, has visto cómo ha cortado a ese en dos!»', 'placa': 'Te pone nervioso cada vez que mira dentro de tu bolsa.'}),
]
ROSA = dict(slug='rosa', n='Rosa Muk, «La Novia Escarlata»', color='#C8102E', arq='Novia con subfusil · reserva', lema='«Nadie arruina mi boda y sale vivo.»',
  fue=11, des=14, vol=13, pg=6, pepitas=50,
  aspecto='Vestido de novia rojo tradicional con bordados de oro, velo desgarrado, moño atravesado por una horquilla de plata y un subfusil atado al muslo.',
  inv=dict(pata='subfusil', torpe='horquilla', c1='lista', c2='vestido-rojo', m1='sobre-rojo'),
  lista=['sheng', 'tonyma', 'oren', 'budd', 'bill'],
  tec=[('Ira furiosa', 'Si tu ataque anterior hizo solo 1 o 2 de daño (o se lo tragó el escudo de Masillas de un jefe), el de este turno hace +3.'),
       ('No me des la espalda', 'Si ningún enemigo te ha atacado desde tu último turno, tu siguiente ráfaga tiene Ventaja (2d8, el mayor) y +1.')],
  op=[dict(id='ira', n='Ira furiosa (+3)', plano=3), dict(id='espalda', n='No me des la espalda (Ventaja, +1)', ventaja=True, plano=1)],
  cuando='Al primer jugador cuyo ratón caiga muerto o incapacitado. En el Acto I toma a Rosa en el mismo banquete; al empezar el Acto II, Rosa se suelta en la Jaula de Bambú con la horquilla oculta en el moño y salta a la pelea.',
  vinculo='Siento decirte que tu ratón ha caído… pero la novia acaba de soltarse las cuerdas. Eres Rosa Muk, oficial de élite de los Tigres Voladores de la Guardia Ratonil y antigua discípula que escapó de la sombra de Bill Jang. Hoy era el día de tu boda con León Yan. Esos bastardos han destrozado tu banquete, han tiroteado a tus amigos, han robado el Sobre Rojo de tu familia y te han metido en una jaula de bambú como a un canario. Coge el subfusil y enséñales por qué el vestido de novia tradicional es rojo sangre.',
  opina={})
TODOS = PJ + [ROSA]
COLORES = {p['slug']: p['color'] for p in TODOS}
NOMBRE = {**{p['slug']: p['n'] for p in TODOS}, **{n['slug']: n['n'] for n in PNJ}}
PNJ_POR = {n['slug']: n for n in PNJ}


def lista_txt(p):
    """Los cinco nombres tal como los escribe el ratón: el n.º 5 en mayúsculas."""
    return [('BILL «MANDÍBULA» JANG' if s == 'bill' else NOMBRE[s]) for s in p['lista']]


# ---------------------------------------------------------------- secuencias de iniciativa (valores fijos de los PNJ)
SECUENCIAS = {
 1: [('rosa', 'Rosa Muk', (14, 14, 11, 12)), ('tonyma', 'Tony Ma', (11, 10, 8, 12)), ('sheng', '«Jet-Set» Sheng', (10, 9, 11, 8)),
     ('turba', 'Turba de Farolillos Azules', (9, 8, 10, 11)), ('alas', '«Alas» Chu (5+ jugadores)', (8, 11, 9, 7)),
     ('leung', '«Ochenta y Ocho» Leung (6 jugadores)', (6, 9, 8, 7)), ('leon', 'León Yan', (6, 9, 10, 11))],
 2: [('bill', 'Bill «Mandíbula» Jang', (13, 12, 12, 11)), ('rosa', 'Rosa Muk (liberada)', (13, 10, 11, 10)), ('leon', 'León Yan (liberado)', (11, 7, 11, 6)),
     ('budd', 'Budd «El Sapo»', (10, 12, 9, 12)), ('turba', 'Guardia de los 88 Maníacos', (9, 7, 8, 11)), ('oren', 'O-Ren «La Tigresa»', (8, 9, 12, 12))],
}

# ---------------------------------------------------------------- tablas
TABLAS = {
 'pelea1': dict(n='Cosas que pasan en la Pelea I', dado='1d10', cols=('Giro', 'En la mesa'), filas=[
  ('Estampado contra el bufé', 'Alguien sale volando de espaldas y aterriza sobre una mesa repleta de arroz, salsas y bandejas, que se parte en dos.'),
  ('Sillazo en la coronilla', 'Una silla plegable de alambre se hace añicos sobre una cabeza: +2 de daño o +2 Masillas abatidos.'),
  ('Se desploma el pabellón', 'Ceden los postes de palillo lacado y la gran lona roja cae sobre la refriega: 1d6 Masillas quedan atrapados debajo.'),
  ('Chapuzón con las carpas', 'Alguien hunde el hocico de su rival bajo el agua del estanque, cara a cara con una carpa koi descomunal.'),
  ('Estatua dorada hecha trizas', 'Una estatua de purpurina revienta cuando estampan a un matón contra ella o la barre una ráfaga: lluvia de yeso dorado.'),
  ('Deslizamiento por el mantel', 'Un héroe cruza una mesa entera deslizándose, barre los centros de flores y remata con una bandeja a la jeta del enemigo.'),
  ('Tetera hirviendo a la cara', 'Una tetera de dedal llena de té verde vuela al hocico de un oponente: queda cegado hasta su siguiente turno.'),
  ('La ira del jefe de catering', 'Cocineros y camareros salen con cucharones insultando a los héroes por destrozar la disposición del banquete.'),
  ('Lluvia de Sobres Rojos', 'Docenas de sobres con pepitas salen volando; media boda se tira de rodillas a rapiñarlos entre los tiros.'),
  ('El velo manchado de pólvora', 'Una ráfaga parte un farolillo colgante, que cae soltando chispas justo cuando un PJ tacha su primer nombre.')]),
 'pelea2': dict(n='Cosas que pasan en la Pelea II', dado='1d12', cols=('Giro', 'En la mesa'), filas=[
  ('Cartuchera que estalla', 'Al caer un Maníaco, su cinturón de petardos de fósforo revienta en una lluvia de chispas rojas y humo.'),
  ('Trampilla de tatami', 'El Maníaco abatido cae sobre un panel falso que se pliega hacia dentro y se lo traga de golpe.'),
  ('Grito hacia el abismo', 'Un enemigo sale despedido por encima de la barandilla y cae gritando hacia las aguas negras del canal.'),
  ('Onda que apaga las velas', 'Un golpe a bocajarro levanta una ráfaga que apaga de golpe toda una hilera de velas de cumpleaños.'),
  ('Ballet a cámara lenta', 'El tiempo se congela: chispas, vainas de latón y gotas rojas se cruzan en el aire entre dos combatientes.'),
  ('El aliento de dragón de Bill', 'Bill da una calada a su cigarrillo de pólvora aromática y escupe una llamarada de alcohol. Solo es teatro: no hace daño.'),
  ('Columna que estalla como cristal', 'Estampan a alguien contra una columna que parece granito y revienta en mil cristales brillantes.'),
  ('El suelo cede', 'Las tablas podridas bajo el tatami se abren y dejan a la vista una caída vertical al canal subterráneo.'),
  ('Chispazo en el altar', 'Justo cuando un PJ tacha su n.º 4, un cable de la pila de 9 V pega un chispazo atronador contra el altar del Fénix.'),
  ('El tatami arde', 'Una bengala caída prende el alcohol derramado: un sector del suelo queda envuelto en llamas bajas.'),
  ('Fuga de hielo seco', 'Un tajo rebana la manguera del humidificador del techo: vigas y máscaras se cubren de escarcha y niebla helada.'),
  ('Siluetas sobre fondo azul', 'El foco principal da un fogonazo blanco y salta: toda la sala queda recortada en siluetas negras sobre luz azul eléctrica.')]),
 'sentencias': dict(n='Sentencias antes de tachar un nombre', dado='1d6', cols=('Frase',), filas=[
  ('«Te lo dije en el banquete: estás en mi cuaderno.»',), ('«Uno menos. Quedan cuatro.»',), ('«Esto es por los bigotes que me cortaste.»',),
  ('«No es personal. Bueno, sí. Es muy personal.»',), ('«Saluda a Bill de mi parte. Enseguida baja.»',), ('«Tenías que haberme rematado.»',)]),
 'postcreditos': dict(n='Escenas postcréditos', dado='1d6', cols=('Corte a negro',), filas=[
  ('En un asiento de primera de un tren de juguete rumbo al norte, una ratona con mono amarillo tacha el quinto nombre de su cuaderno, sonríe y pide un platito de leche tibia.',),
  ('En el Jardín del Estanque Koi, el jefe de catering sigue de rodillas pegando con cola los trozos de una estatua dorada y jura no volver a servir una boda de policías.',),
  ('En un taller oculto tras una máquina de coser, el viejo armero Hattori Ratzo limpia una hoja de bisturí con un paño de seda: ha vuelto a romper su juramento… por una buena causa.',),
  ('Rosa Muk y León Yan se hacen las fotos oficiales de boda ante las ruinas humeantes de La Casa de las Hojas Azules, ella todavía con la cinta de munición cruzada sobre el vestido rojo.',),
  ('En la comisaría de la Guardia, un inspector novato abre una taquilla y encuentra seis expedientes con una sola palabra estampada en rojo: «SALDADO».',),
  ('En el fondo del estanque del jardín, una carpa koi gigante nada plácidamente con el antifaz negro de uno de los 88 Maníacos en la boca.',)]),
}
# Armas para la tabla del arsenal, en orden
ARSENAL = ['kungfu', 'nunchakus', 'katana', 'bate', 'estrellas', 'chispero', 'pistola-pesada', 'magnum', 'subfusil', 'escopeta', 'rifle-aguja', 'petardos']
