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

Per percorso migliore, in questo caso, si intende il percorso che mi porti a destinazione nel minor tempo possibile.


## Elenco argomenti di interesse

* **Condivisione della conoscenza**: utilizzo di ontologie per attribuire significato al dataset, rappresentazione con *RDF XLM* ed estrazione di dati con un parser XLM.
* **Rappresentazione e ragionamento relazionale**: caricamento di dati in una base di conosceza in *Prolog* con inferenze sulla conoscenza per ricavare i dati per la ricerca sul grafo.
* **Risoluzione di problemi mediante ricerca**: Utilizzo di *A** con la tecnica del *Multi Path Pruning* per evitare cicli.

## Condivisione della conoscenza

L'ontologia è la specifica dei concetti all'interno di un dominio.
Attribuisce un significato ai termini utilizzati e le relazioni tra di esse.

Vengono utilizzate per permettere l'utilizzo dei dati indipendentemente dall'applicazione interessata.

Le ontologie vengono mantenute dalle community che le usano.

L'ontologia utilizzata nel progetto è quella di [Open Street Map](https://www.openstreetmap.org/) descritta in *RDF*. 

Il framework *RDF* è utilizzato per la rappresentazione dei dati sul web.
Consiste di rappresentare dati attraverso tuple `<soggetto><predicato><oggetto>`.

### Sommario

Sono stati utilizzati diversi concetti dall'ontologia.

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
Cosi riprendendo l'esempio di un cammino rettilineo di 1000m, avremo 2 nodi piuttosto che 1000.

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

1. La distanza non è calcolata in base al numero di archi coinvolti 
2. Tutti i nodi che generano intersezioni rimangono nel grafo, lasciandolo connesso.






