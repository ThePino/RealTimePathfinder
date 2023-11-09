# RealtimePathFinder

## Gruppo di lavoro

| Nominativo     | Matricola | Email                       |
|----------------|-----------|-----------------------------|
| Giacomo Gaudio | 715894    | g.gaudio7@studenti.uniba.it |

[Repository al materiale completo](https://github.com/ThePino/RealTimePathfinder).

AA 2022-2023

## Introduzione

In astratto questo caso di studio si propone di trovare il percorso ottimale in un grafo tra una coppia di nodi
considerando che col passare del tempo la possibilità di attraversare un arco vari nel tempo.

Il dominio specifico prende in considerazione lo spostamento in auto in una città e l'esigenza di arrivare a una
determinata posizione.

Durante il percorso verso destinazione, causa incidenti o manifestazioni, certe strade diventino impercorribili
ed è necessario cambiare strada.
Col passare del tempo, è possibile che strade precedentemente bloccate siano di nuovo attraversabili fornendo un percorso
migliore.
Tutti queste modifiche di operabilità sulle strade prendono il nome di **events**.

Per percorso migliore, in questo caso, si intende il percorso che mi porti a destinazione nel minor tempo possibile.


## Elenco argomenti di interesse

* **Condivisione della conoscenza**: utilizzo di ontologie per attribuire significato al dataset, rappresentazione con *RDF XML* ed estrazione di dati con un parser XML.
* **Rappresentazione e ragionamento relazionale**: caricamento di dati in una base di conosceza in *Prolog* con inferenze sulla conoscenza per ricavare i dati per la ricerca sul grafo.
* **Risoluzione di problemi mediante ricerca**: Utilizzo di *A** con la tecnica del *Multi Path Pruning* per evitare cicli.

## Condivisione della conoscenza

L'ontologia è la specifica dei concetti all'interno di un dominio.
Attribuisce un significato ai termini utilizzati e le relazioni tra di esse.

Vengono utilizzate per permettere l'utilizzo dei dati indipendentemente dall'applicazione interessata.

Le ontologie vengono mantenute dalle community che le usano.

### Sommario

L'**ontologia** utilizzata nel progetto è quella di [Open Street Map](https://www.openstreetmap.org/) descritta in *RDF*.
Nella cartella `resources/open_street_map` è presente il file 'ontology.ttl' contenente l'ontologia.

Il framework *RDF* è utilizzato per la rappresentazione dei dati sul web.
Consiste di rappresentare dati attraverso tuple `<soggetto><predicato><oggetto>`.

Sono stati diversi concetti dell'ontologia *osm*.

#### node

Il concetto di `node` è un punto nello spazio caratterizzato da lattitude e longitude.
Utilizzato all'interno del progetto per mappare la città in nodi.

```rdf
osm:Node
        a                     rdfs:Class , owl:Class ;
        rdfs:comment          """A node is one of the core elements in the OpenStreetMap data model.
                              It consists of a single point in space defined by its latitude, longitude and node id."""@en ;
        rdfs:label            "Node"@en ;
        rdfs:subClassOf       geo:Point ;
        owl:disjointWith      osm:Way , osm:Relation ;
        rdfs:isDefinedBy      osm: ;
        prov:wasInfluencedBy  <https://wiki.openstreetmap.org/wiki/Node> .
```

Esempio di un elemento nodo:

```xml
<node id="5092766368" visible="true" version="2" changeset="122438107" timestamp="2022-06-15T23:13:38Z" user="Giovanni Forgione" uid="11403185" lat="40.6361763" lon="14.6028394"/>
```

#### Way

Il concetto di `way` è utilizzato per rappresentare una strada come un elenco ordinato di `node`.
Utilizzato all'interno del progetto per creare gli archi tra i nodi.

```rdf
osm:Way
        a                     rdfs:Class , owl:Class ;
        rdfs:comment          "A way is an ordered list of nodes which normally also has at least one tag."@en ;
        rdfs:label            "Way"@en ;
        owl:disjointWith      osm:Node , osm:Relation ;
        rdfs:isDefinedBy      osm: ;
        prov:wasInfluencedBy  <https://wiki.openstreetmap.org/wiki/Way> .
```

Esempio di un elemento `way`:

```xml
<way id="1213086878" visible="true" version="1" changeset="142154502" timestamp="2023-10-04T16:34:12Z" user="Fogey7" uid="11127047">
  <nd ref="11238720363"/>
  <nd ref="11238720362"/>
  <nd ref="11238720361"/>
  <nd ref="11238720364"/>
  <tag k="highway" v="footway"/>
 </way>
```

#### highway, HighwayValue

L'elemento `highway` definisce di che tipologia è una strada.
L'elemento `HighwayValue` definisce i possibili valori.

L'elemento `highway` è stato utilizzato nel progetto per discriminare gli elementi `way` che non sono strade.
L'elemento `HighwayValue` è stato utilizzato nel progetto per discriminare gli elementi `way` che sono strade
percorribili dalle auto.

```rdf
osm:highway
        a                      owl:ObjectProperty , rdf:Property ;
        owl:equivalentProperty <http://www.wikidata.org/entity/Q57977870> ;
        rdfs:comment           "The kind of road, street or path."@en ;
        rdfs:label             "highway=*"@en ;
        rdfs:isDefinedBy       osm: ;
        prov:wasInfluencedBy   <https://wiki.openstreetmap.org/wiki/Key:highway> ;
        rdfs:domain            [ owl:unionOf    (osm:Node osm:Way) ] ;
        rdfs:range             osm:HighwayValue .

 osm:HighwayValue
        a                     rdfs:Class , owl:Class ;
        rdfs:comment          "The kind of road, street or path."@en ;
        rdfs:label            "HighwayValue"@en ;
        rdfs:isDefinedBy      osm: ;
        prov:wasInfluencedBy  <https://wiki.openstreetmap.org/wiki/Key:highway> .
```

Esempio di elemento `highway` e `HighwayValue`.

```xml
<way id="1213086878" visible="true" version="1" changeset="142154502" timestamp="2023-10-04T16:34:12Z" user="Fogey7" uid="11127047">
  <nd ref="11238720363"/>
  <nd ref="11238720362"/>
  <nd ref="11238720361"/>
  <nd ref="11238720364"/>
  <tag k="highway" v="footway"/>
 </way>
```

#### oneway, OnewayValue

L'elemento `oneway` definisce in che modo gli elementi `node` del elemento `way` devono essere considerati.
L'elemento `OnewayValue` definisce l'ordine con cui analizzare la lista (direzionale, bidirezionale, inverso).
```rdf
osm:oneway
        a                      owl:ObjectProperty , rdf:Property ;
        owl:equivalentProperty <http://www.wikidata.org/entity/Q786886> ;
        rdfs:comment           "The direction restrictions on highways."@en ;
        rdfs:label             "oneway=*"@en ;
        rdfs:isDefinedBy       osm: ;
        prov:wasInfluencedBy   <https://wiki.openstreetmap.org/wiki/Key:oneway> ;
        rdfs:domain            osm:Way ;
        rdfs:range             osm:OnewayValue .
        
osm:OnewayValue
        a                     rdfs:Class , owl:Class ;
        rdfs:comment          "Direction restrictions."@en ;
        rdfs:label            "OnewayValue"@en ;
        rdfs:isDefinedBy      osm: ;
        prov:wasInfluencedBy  <https://wiki.openstreetmap.org/wiki/Key:oneway> .        
```

Esempio di un elemento `oneway` e `OnewayValue`.

```xml
<tag k="oneway" v="yes"/>
```

#### maxspeed

L'elemento `maxspeed` definisce la velocità massima percorribile in km/h.
Utilizzata nel progetto per indicare la velocità massima per attraversare un arco.

```rdf
osm:maxspeed
        a                     owl:DatatypeProperty , rdf:Property ;
        rdfs:comment          "The maximum legal speed limit, in km/h."@en ;
        rdfs:label            "maxspeed=*"@en ;
        rdfs:isDefinedBy      osm: ;
        prov:wasInfluencedBy  <https://wiki.openstreetmap.org/wiki/Key:maxspeed> ;
        qudt:hasUnit          unit:KM-PER-HR ;
        rdfs:domain           osm:Way ;
        rdfs:range            xsd:double .

```

Un esmpio di elemento `maxspeed`:

```xml
<tag k="maxspeed" v="10"/>
```

#### tag

Il concetto di tag non è esplicitato direttamente. Ma è utilizzato per collegare le proprietà `oneway`, `maxspeed`, e `highway`
agli elementi `node` e `way`.


### Strumenti utilizzati

Per ricavare i dati correlati all'ontologia, si è utilizzata la funzione esporta dal sito web [open street map](https://www.openstreetmap.org) scegliendo la città desiderata.

I dati scaricati sono strutturati in *XML*. 

I dati scaricati sono presenti in 'resource/open_street_map/atrani.osm'.
È presente anche il file 'resource/open_street_map/test.osm' utilizzato come test durante lo sviluppo.

### Decisioni di progetto

Per l'importazione dei dati scaricati in *XML* è stata utilizzata la libreria `xml` default di python.

Il servizio addetto al parsing del file di open street map è nella cartella del progetto `src/service/data/osm_xml_parser.py`.

Ha il compito di importare i dati e trasformarli in oggetti più maneggevoli a livello di codice.
Il modello python adoperato è situato nella cartella del progetto `src/model/osm`.

Un ulteriore compito è quello di filtrare i dati.

Un primo filtraggio avviene sugli elementi `way` scartando tutti le strade non percorribili dalle auto.

Il filtraggio avviene basandosi sulle proprietà dell'elemento `way`, indicati tramite tag, avente come chiave `highway`.
I valori ammessi per `highway` sono definti all'interno del codice in `src/model/way` nella enumerazione `HighwayOSMEnum`.
I valori indicati nell' enumerazione, sono stati scelti dai possibili valori indicati dall'elemento `HighwayValue` che
indicava una percorrenza possibile per le auto.

Un secondo filtraggio è necessario per ridurre le dimensioni del grafo. 

Lo sviluppo python ha limitazione sulla profondità delle chiamate ricorsive e cammini lunghi superano il limite massimo
dello stack consentito.
L'implementazione della classe `Path` fornita da [AIPython](https://artint.info/AIPython/) fa uso
di chiamate ricorsive, e con cammini di 300 nodi e più, l'ambiente python non riesce a elaborarli.

I dati di open street map sono molto precisi, la distanza tra due nodi può anche essere meno di un metro; considerando
una media di un nodo al metro, su 1000 metri si avranno 1000 nodi.
La semplificazione del grafo adottata è quella di rimuovere i nodi intermedi che non hanno intersezioni.
Riprendendo l'esempio di un cammino rettilineo di 1000m, avremo 2 nodi piuttosto che 1000.

Esempio grafico:

```text
# Esempio di grafo prima della semplificazione

A - B - C - D - E - F
|       |
G       H

# Dopo la semplificazione..

A - C - F
|   |
G   H
```

Questa semplificazione è giustificata da due fattori:

1. Il percorso ottimale non dipende dal numero di archi attraversati.
2. Tutti i nodi che generano intersezioni rimangono nel grafo, lasciandolo connesso.

Per le limitazioni di Python, la città in esame scelta è [Atrani](https://it.wikipedia.org/wiki/Atrani).
Una delle più piccole città d'Italia.

#### events?

Nell'ontologia di *osm* non sono definiti gli eventi. 

Un evento è un elemento definito appositamente per la realizzazione del progetto.
È caratterizzato da due attributi:

* **time**: l'unità di tempo in milli secondi in cui accade un evento.
* **way**: l'identificativo dell'arco che cambia stato.

Al tempo indicato, lo stato dell'arco identificato viene invertito. 
Se prima era possibile attraversarlo, ora non è più possibile.
Se prima non era possibile attraversarlo, ora è possibile.

All'inizio, ogni arco è attraversabile.

Per garantire una finitezza dell'algoritmo, il numero di eventi per ogni arco coinvolto deve essere pari.
In modo tale da ripristinare lo stato di attraversabile.

Non è stata realizzata un estensione dell'ontologia *osm* perché non si ha necessità di condividere tale informazioni
con fonti esterne al progetto.

Gli eventi vengono importati dal servizio in 'src/service/data/event_xml_parser.py' presenti nel path 'resources/event/event.xml'.
Nello steso percorso è disponibile 'event_test.xml' utilizzato durante lo sviluppo.

## Rappresentazione e ragionamento relazionale

Una **Knowledge Base** è un sistema che organizza informazioni in modo strutturato e accessibile.

È progettata per immagazzinare dati e agevolare il loro utilizzo da parte di programmi o agenti intelligenti.

Questo sistema rappresenta la memoria a lungo termine di un agente, conservando la conoscenza necessaria per future azioni.

La **Knowledge Base** è solitamente creata offline da esperti di conoscenza e dati che collaborano nella sua costruzione.

### Sommario

La base di conoscenza è strutturata in fatti e regole.

I fatti sono i dati a disposizione della base di conoscenza per poter effettuare inferenze attraverso le regole.

#### Fatti 

Per strutturare i fatti ho mantenuto la struttura del framework **rdf** (soggeto, predicato, oggetto).

All'interno è presente una sola procedura con i 3 parametri chiamata 'prop' che permette di definire i fatti.

I dati estratti dall'ontologia sono stati plasmati nelle classi `node` e `way`.

##### node

La classe `node` modella un nodo nel grafo.

| Attributo | Definizione                        |
|-----------|------------------------------------|
| type      | identifica di che tipo è la classe |
| lat       | indica la lattitude del nodo       |
| long      | indica la longitude del nodo       |

Un esempio di definizione di `node`:

```prolog
prop(node0, type, node).
prop(node0, lat, 0).
prop(node0, lon, 0).
```

##### way

La classe `way` modella un arco nel grafo.

| Attributo | Definizione                                                                      |
|-----------|----------------------------------------------------------------------------------|
| type      | identifica di che tipo è la classe                                               |
| from_node | indica il nodo di partenza dell'arco                                             |
| to_node   | indica il nodo di arrivo dell'arco                                               |
| max_speed | indica la velocità massima in km che si può attraversare l'arco                  |
| available | indica se l'arco è attraversabile. 'true' per atterversabile, 'false' altrimenti |

Un esempio di definizione di `way`:

```prolog
prop(way0, type, way).
prop(way0, from_node, node0).
prop(way0, to_node, node1).
prop(way0, max_speed, 10).
prop(way0, available, true).
```

#### Regole 

Le regole permettono di effettuare inerenze sulla base di dati.

Sono state definite le seguenti regole:

##### is_node(X)

La regola che indica se nome è un nodo.
```prolog
is_node(X):-
    prop(X, type, node).
```

##### get_node_coord(X, Lat, Lot)

Regola che restituisce le coordinate di un nodo.

```prolog
get_node_coord(X, Lat, Lot):-
    is_node(X),
    prop(X, lat, Lat),
    prop(X, lon, Lot).
```

##### is_way(X)

Regola che indica se un nome è un arco.

```prolog
is_way(X):-
    prop(X, type, way).
```

##### is_available(Way)

Regola che indica se un arco è attraversabile.

```prolog
is_available(Way) :-
    is_way(Way),
    prop(Way, available, true).
```

##### set_available_attribute(Way, Available) 

Regola che cambia lo stato della base di conoscenza per aggiornare lo stato di un arco.

```prolog
set_available_attribute(Way, Available) :-
    is_way(Way),
    retract(prop(Way, available, _)), % Remove the old available attribute
    assertz(prop(Way, available, Available)). % Assert the updated available attribute
```

##### get_all_way_ids(Way)

Regola che restituisce tutti i nomi associati agli archi.

```prolog
get_all_way_ids(Way):-
    is_way(Way).
```

##### get_all_node(Node, Lat, Lon)

Regola che restituisce tutti i nodi presenti.
Nel progetto è stata utilizzata per scegliere i due nodi geograficamente più distanti per far iniziare la ricerca del percorso.

```prolog
get_all_node(Node, Lat, Lon):-
    is_node(Node),
    prop(Node, lat, Lat),
    prop(Node, lon, Lon).
```

#### get_ways(Way, From_node, To_node)

Regola che restituisce tutti gli archi fissato un nodo.

```prolog
get_ways(Way, From_node, To_node):-
    is_way(Way),
    prop(Way, from_node, From_node),
    prop(Way, to_node, To_node).
```


#### get_available_ways(Way, From_node, To_node)

Regola che restituisce tutte le strade disponibili fissato un nodo.

```prolog
get_available_ways(Way, From_node, To_node):-
    get_ways(Way, From_node, To_node),
    is_available(Way).
```

#### get_max_speed_way(Way, X)

Regola che restituisce la velocità di un arco.

```prolog
get_max_speed_way(Way, X):-
    is_way(Way),
    prop(Way, max_speed, X).
```

#### get_max_speed_from_nodes(From_node, To_node, Max_speed)

Regola che restituisce la velocità dell'arco fissato i due nodi.

```prolog
get_max_speed_from_nodes(From_node, To_node, Max_speed):-
    get_available_ways(Way, From_node, To_node),
    get_max_speed_way(Way, Max_speed).
```

#### get_way_all_info_available(From_node, To_node, To_node_lat, To_node_lon, Max_speed)

Regola che restituisce tutte le info sulle adiacenze del nodo fissato.

```prolog
get_way_all_info_available(From_node, To_node, To_node_lat, To_node_lon, Max_speed):-
    get_available_ways(Way, From_node, To_node),
    get_max_speed_way(Way, Max_speed),
    get_node_coord(To_node, To_node_lat, To_node_lon).
```

### Strumenti utilizzati

È stato utilizzato [SWI-Prolog](https://www.swi-prolog.org/) come ambiente prolog e interfaccia per testare le regole durante lo sviluppo.


### Decisioni di progetto

È stata utilizzata la libreria `pyswip` per interagire con prolog.

Un limite di tale libreria è la definizione di fatti a runtime. 
Per rimediare a tale limitazione, i fatti sono stati scritti su file e successivamente caricati attraverso la funzione `consult`.

I fatti sono stati scritti dal servizio in `src/service/data/facts_writer` utilizzando i dati importati dal modello *osm*.
Il file in cui vengono scritti i file è in `resources/prolog/facts.pl`.

Le regole sono state scritte a mano.
Il file in cui sono scritte le regole è in `resources/prolog/rules.pl`.
Dovendo modificare a run time un fatto, è stato necessario aggiungere la seguente linea di codice alle regole `:- dynamic prop/3.`

È stato realizzato il servizio in `pyswip_client` per astrarre le query con prolog.
Il modello risultate dalle query prolog è in `src/model/prolog`. 

## Risoluzione di problemi mediante ricerca

### Sommario 


### Strumenti utilizzati 

