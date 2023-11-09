# RealtimePathFinder

## Gruppo di lavoro

| Nominativo     | Matricola | Email                       |
|----------------|-----------|-----------------------------|
| Giacomo Gaudio | 715894    | g.gaudio7@studenti.uniba.it |

[Repository al materiale completo](https://github.com/ThePino/RealTimePathfinder).

AA 2022-2023

## Introduzione

Questo caso di studio si propone di trovare il percorso minimo tra una coppia di nodi in un grafo dove la possibilità di attraversare ogni arco può variare nel tempo.

Il dominio specifico prende in considerazione lo spostamento in auto in una città, con l'esigenza di arrivare a una determinata destinazione.

Durante il percorso verso la destinazione, certe strade possono diventare impercorribili causa incidenti o manifestazioni, ed è necessario cambiare percorso.
Col passare del tempo, è possibile che strade precedentemente bloccate siano di nuovo attraversabili rientrando nel percorso
migliore.
Tutte queste modifiche di operabilità sulle strade prendono il nome di **events**.

Per percorso migliore, in questo caso, si intende il percorso che mi porti a destinazione nel minor tempo possibile.


## Elenco argomenti di interesse

* **Condivisione della conoscenza**: utilizzo di ontologie per attribuire significato al dataset, rappresentazione con *RDF XML* ed estrazione di dati con un parser XML.
* **Rappresentazione e ragionamento relazionale**: caricamento dei dati in una base di conoscenza in *Prolog* con inferenze sulla conoscenza per ricavare i dati per la ricerca sul grafo.
* **Risoluzione di problemi mediante ricerca**: Utilizzo di *A** con la tecnica del *Multi Path Pruning*.

## Condivisione della conoscenza

L'ontologia è la specifica dei concetti all'interno di un dominio.
Attribuisce un significato ai simboli utilizzati e le relazioni tra di essi.

Vengono utilizzate per permettere la condivisione dei dati indipendentemente dall'applicazione interessata.

Le ontologie vengono sviluppate in accordo con le community che sono coinvolte con il dominio d'interesse.

### Sommario

L'**ontologia** utilizzata nel progetto è quella di [Open Street Map](https://www.openstreetmap.org/) descritta in *RDF*.
Nella cartella `resources/open_street_map` è presente il file `ontology.ttl` contenente l'ontologia.

Il framework *RDF* è utilizzato per condivisione di informazioni nel web semantico.
Consiste nel rappresentare le informazioni attraverso triple `<individuo><proprietà><valore>`.

Sono stati utilizzati diversi elementi dell'ontologia *osm*.

#### node

Il concetto di `node` è un punto nello spazio caratterizzato da lattitude e longitude.
Utilizzato all'interno del progetto per mappare la posizione geografica del inizio, intersezioni e fine delle strade della città.

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
<way id="1213086878" >
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
<way id="1213086878">
  <nd ref="11238720363"/>
  <nd ref="11238720362"/>
  <nd ref="11238720361"/>
  <nd ref="11238720364"/>
  <tag k="highway" v="footway"/>
 </way>
```

#### oneway, OnewayValue

L'elemento `oneway` definisce in che modo gli elementi `node` del elemento `way` devono essere interpretati.
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
Utilizzata nel progetto per indicare la velocità massima ammessa su quella strada.

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

I dati scaricati sono strutturati in *RDF XML*. 

I dati scaricati sono presenti in `resource/open_street_map/atrani.osm`.
È presente anche il file `resource/open_street_map/test.osm` utilizzato come test durante lo sviluppo.

### Decisioni di progetto

Per l'importazione dei dati scaricati in *RDF XML* è stata utilizzata la libreria `xml` default di python.

Il servizio addetto al parsing del file di open street map è nella cartella del progetto `src/service/data/osm_xml_parser.py`.

Ha il compito di importare i dati e trasformarli in oggetti più maneggevoli a livello di codice.
Il modello python adoperato è situato nella cartella del progetto `src/model/osm`.

Un ulteriore compito svolto è quello di filtrare i dati.

Un primo filtraggio avviene sugli elementi `way` scartando tutti le strade non percorribili dalle auto.

Il filtraggio avviene basandosi sulle proprietà dell'elemento `way`, indicati tramite tag, avente come chiave `highway`.
I valori ammessi per `highway` sono definti all'interno del codice in `src/model/way` nella enumerazione `HighwayOSMEnum`.
I valori indicati nell' enumerazione, sono stati scelti dai possibili valori indicati dall'elemento `HighwayValue` che
indica una percorrenza possibile per le auto.

Un secondo filtraggio è necessario per ridurre le dimensioni del grafo. 

Lo sviluppo python ha limitazione sulla profondità delle chiamate ricorsive e cammini lunghi superano il limite massimo
dello stack consentito.
L'implementazione della classe `Path` fornita da [AIPython](https://artint.info/AIPython/) fa uso
di chiamate ricorsive, e con cammini di 300 nodi e più, l'ambiente python non riesce a elaborarli.

I dati di open street map sono molto precisi, la distanza tra due nodi può anche essere meno di un metro; considerando
una media di un nodo al metro, su 1000 metri si avranno 1000 nodi.
La semplificazione del grafo adottata è quella di rimuovere i nodi intermedi che non sono intersezioni.
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

Questa semplificazione è giustificata da tre fattori:

1. Il percorso ottimale non dipende dal numero di archi attraversati.
2. Tutti i nodi che sono di intersezione rimangono nel grafo, lasciandolo connesso.
3. Se vi è un evento che impedisce la possibilità di attraversa un arco intermedio basta disabilitare l'arco che lo include. 

Per le limitazioni di Python, la città in esame scelta è [Atrani](https://it.wikipedia.org/wiki/Atrani).
Una delle più piccole città d'Italia.

#### events?

Nell'ontologia di *osm* non sono definiti gli eventi. 

Un evento è un elemento definito appositamente per la realizzazione del progetto.
È caratterizzato da due attributi:

* **time**: l'unità di tempo in milli secondi in cui accade l'evento.
* **way**: l'identificativo dell'arco che cambia stato.

Al tempo indicato, lo stato dell'arco identificato viene invertito. 
Se prima era possibile attraversarlo, ora non è più possibile.
Se prima non era possibile attraversarlo, ora è possibile.

All'inizio, ogni arco è attraversabile.

Per garantire una finitezza dell'algoritmo, il numero di eventi per ogni arco coinvolto deve essere pari.
In modo tale da ripristinare lo stato di attraversabile.

Non è stata realizzata un' estensione dell'ontologia *osm* perché non si ha necessità di condividere tale informazioni
con fonti esterne al progetto.

Gli eventi vengono importati dal servizio in `src/service/data/event_xml_parser.py` presenti nel path `resources/event/event.xml`.
Nello steso percorso è disponibile `event_test.xml` utilizzato durante lo sviluppo.

## Rappresentazione e ragionamento relazionale

Una **Knowledge Base** è un insieme di conoscenze organizzate in modo strutturato.

È progettata per immagazzinare conoscenze e agevolare il loro utilizzo da parte di programmi o agenti intelligenti.

Questo sistema rappresenta la memoria a lungo termine di un agente, conservando la conoscenza necessaria per future azioni.

La **Knowledge Base** è solitamente creata offline da esperti di conoscenza che collaborano nella sua costruzione.

### Sommario

La base di conoscenza è strutturata in fatti e regole.

I fatti sono la conoscenza primitiva a disposizione della KB per poter derivare conoscenza attraverso le regole.

#### Fatti 

Per strutturare la conoscenza in maniera più omogenea ho utilizzato la rappresentazione individuo, proprietà, valore avvicinandomi così alla struttura di triple del framework **rdf**.

All'interno è presente una sola relazione con i 3 parametri chiamata 'prop' che permette di definire i fatti.

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
| available | indica se l'arco è attraversabile. 'true' per attraversabile, 'false' altrimenti |

Un esempio di definizione di `way`:

```prolog
prop(way0, type, way).
prop(way0, from_node, node0).
prop(way0, to_node, node1).
prop(way0, max_speed, 10).
prop(way0, available, true).
```

#### Regole 

Le regole permettono di effettuare inferenza sulla KB.

Sono state definite le seguenti regole:

##### is_node(X)

La regola che indica se X è un nodo.

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

Regola che indica se X è un arco.

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

Regola che restituisce tutti gli archi.

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

Regola che restituisce la velocità dell'arco fissati i due nodi.

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

I fatti sono stati scritti dal servizio in `src/service/data/facts_writer.py` utilizzando i dati importati dal modello *osm*.
Il file in cui vengono scritti i fatti è in `resources/prolog/facts.pl`.

Le regole sono state scritte a mano.
Il file in cui sono scritte le regole è in `resources/prolog/rules.pl`.
Dovendo modificare a run time un fatto, è stato necessario aggiungere la seguente linea di codice alle regole `:- dynamic prop/3.`

È stato realizzato il servizio in `pyswip_client` per interfacciarsi con le query in prolog.
Il modello risultate dalle query prolog è in `src/model/prolog`. 

## Risoluzione di problemi mediante ricerca

Risolvere i problemi mediante ricerca è una tecnica fondamentale nella ingegneria della conoscenza.

Questa tecnica prevede la formulazione di uno spazio di ricerca, dove vengono esplorate diverse soluzioni per trovare l'ottimale.

Per applicarla è necessario definire uno stato iniziale, una serie di azioni che cambiano il nostro stato e lo stato finale.

Durante il processo di ricerca si possono applicare diversi algoritmi che si distinguono in *ricerca informata* e *ricerca non informata*.
La *ricerca non informata* non hanno conoscenza sulla posizione degli obbiettivi e non possono essere guidati.
La *ricerca informata* ha conoscenza sulla posizione degli obbiettivi e possono essere guidati.

### Sommario 

Il nostro grafo è composto da nodi caratterizzati da latitudine e longitude.

Una coppia di nodi è collegata attraverso un arco che indica anche la velocità massima.

Il costo di attraversamento di un arco è data dal tempo necessario per fare la distanza in km orari dei nodi alla velocità massima consentita.

Per conoscere le adiacenze di un nodo e le caratteristiche dell'arco è possibile interrogare la base di conoscenza.

Lo stato iniziale del nostro problema è il nodo di partenza mentre lo stato finale è il nodo di destinazione.
Le azioni possibili sono quelle di attraversare gli archi ottenuti dalla base di conoscenza.

Conoscendo il nodo di destinazione e partenza ricadiamo nei problemi di ricerca informati ed è possibile utilizzare algoritmo di ricerca informati.
L'algoritmo scelto è `A*`, un miglioramento dell'algoritmo di dijkstra.

La funzione euristica definita è simulare l'esistenza di un arco diretto verso il nodo obbiettivo con la possibilità di 
viaggiare alla velocità massima.
In questo modo non sovrastimiamo il costo effettivo della ricerca e diamo priorità ai nodi geograficamente più vicini al nodo di destinazione.
Questo vale poiché non esisterebbe nessun altro percorso più breve o una serie di percorsi con velocità più alte possibili.

Il calcolo del percorso ottimale viene fatto sullo stato attuale della base di conoscenza.
Pian piano che si segue il percorso ottimale ottenuto da A*, si aggiorna la base di conoscenza e si chiede se l'arco che si sta per attraversare sia disponibile.

Se l'arco è disponibile si attraversa, altrimenti si ricalcola il percorso riapplicando A* sullo stato attuale.

Se A* non restituisce nessun percorso, si simula un'attesa cosi che gli eventi successivi abbiano effetto.

Si ripete fin quando non si arriva a destinazione. 

### Strumenti utilizzati

Sono state utilizzate le classi per la rappresentazione di un problema di ricerca e la sua soluzione provenienti da [IAPython](https://artint.info/AIPython/).
Tali classi sono situate in `src/external_lib`.
I file sono stati modificati dagli originali per rimuovere la stampa a video dello stato della ricerca.

### Decisioni di progetto 

Le funzioni per il calcolo del tempo di percorrenza, della distanza tra due nodi sono in `src/service/util.py`.
Come unità di misura di tempo sono stati scelti i ms poiché i secondi risultavano poco precisi.
Compiere 1m di distanza a 50km/h risulta pari a 0,00002s.

All'algoritmo *A** è stata aggiunta la tecnica del pruning attraverso *MPP*.
Avendo nodi molto vicini geograficamente, percorre una distanza infinitissimamente piccola tra una determinata coppia di nodi risultava ottimale piuttosto che spostarsi su un altro nodo; andando in loop.
Una prima soluzione è stata utilizzare il peso dell'euristica al quadrato ma ciò non la rendeva più ammisibile: il costo dell'euristica superava quello effettivo.
Adoperando il *MPP* si è risolto il problema poiché il percorso restitutio non tornava mai sui suoi vecchi passi.

I servizi che adoperano la ricerca e la definizione del problema sono in `src/service/search` che estendono le classi definite da *IAPython*.

Il simulatore di eventi e del cammino del percorso è definito in `src/service/handler.py`.
Gli eventi sono aggiornati pian piano che si percorre il cammino migliore.

## Conclusioni 

L'obbiettivo di trovare il percorso migliore considerando la modifica sulla percorrenza degli archi è stato raggiunto.

La maggiore difficoltà è stata lavorare con dati reali.
Distanze veramente piccole ad alte velocità hanno creato problemi di loop.

I possibili sviluppi sono:

* Considerare l'elemento *relation* di open street map: abilita a spostamenti a piedi, bici e mezzi pubblici.
* Considerare i segnali di precedenza e stop e semafori: fare il percorso con meno "pause" possibili

