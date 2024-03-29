#Per ovviare al problema delle date in ordine crescente, ho pensato di tenere traccia di un max tra le date, e se andando avanti questo valore NON viene superato, vuol dire che c'è una data fuori posto, e quindi alzo un eccezione.

#******************************
#  Gestione casi speciali
#******************************

#CASO 1
#Se l'anno inziale e l'anno finale coincidono, returno semplicemente l'anno desiderato col suo valore di media. Tuttavia se l'anno inserito è lo stesso ma non presenta alcuna misurazione, viene returnata una lista vuota

#CASO 2
#se l'anno iniziale e finale sono due anni che non presentano dati, ma sono presenti nel file, e hanno in mezzo un anno con dati presenti. ALlora stampo l'anno in mezzo. Esempio 1950 e 1952. Dove 1950 e 1952 non hanno dati, ma 1951 si, stampa quello (1951)

#CASO 3
#se last year passato come parameteo non ha dati al suo interno, interrompe il ciclo. Casistica intervallo '49-'52, dati mancanti 1950 e 1952. Ideologicamente dovrebbe restituire 1949-1950 1950-1951 1951-1952. Ma dato che mancano quei due anni deve restituire 1949-1951 e basta. Questo controllo impedisce di memorizzare anche 1951-1953 che andrebbe oltre il limite alto imposto

#CASO 4
#Gestione caso in cui last_year è maggiore di first_year passati come parametri di compute_elements. Li inverto in modo che funzioni lo stesso

#CASO 5
#Gestione anche che l'anno sia diverso da 0 e che il mese sia compreso fra 1 e 12, altrimenti ignora il dato

#==============================
#  Libreria per regex, utilizzata in get_data() per verificare il pattern della data "YYYY-MM"
#==============================
import re


#inizializzo una lista vuota che conterrà tutti gli anni privi di almeno una misurazione. globale
anni_vuoti = []

#==============================
#  Classe ExamException da usare per istanziare eccezioni
#==============================

class ExamException(Exception):
    pass



#==============================
#  Classe per file CSV
#==============================

class CSVTimeSeriesFile:

    def __init__(self, name):
        
        # Setto il nome del file
        self.name = name

    def get_data(self):

        count = 0
        
        #verifico che il file CSV esista e sia leggibile, altrimenti alzo un eccezione
        try:
            file = open(self.name, 'r')
            file.readline()
        except Exception as e:
            raise ExamException('Impossibile leggere il file "{}". Errore: "{}"'.format(self.name, e))

        #inizializzo la lista di liste che dovrò returnare
        data = []
        
        for line in file:

            # Faccio lo split di ogni linea sulla virgola
            elements = line.split(',')

            # Tolgo il carattere di newline (\n) e gli spazi bianchi agli estremi
            # dall'ultimo elemento con la funzione strip():
            elements[-1] = elements[-1].strip()
            
            # Se non sto processando l'intestazione
            if elements[0] != 'Date':
                
                #Se la data non esiste (stringa vuota, caratteri speciali, non rispecchia il pattern "YYYY-MM")
                if verifica_pattern(elements[0]):
                    try:
                        #Conversione valore in intero
                            elements[1] = int(elements[1])

                            #se il valore è negativo, lo saltiamo
                            if elements[1] < 0:
                                continue


                            #Verifica che l'anno sia diverso da 0 e che il mese sia compreso fra 1 e 12, altrimenti ignora il dato
                        
                            verifica_data_diverso_da_zero = elements[0].split('-')
                            verifica_anno_diverso_da_zero = int(verifica_data_diverso_da_zero[0])
                            verifica_mese_coerente = int(verifica_data_diverso_da_zero[1])
                            if verifica_anno_diverso_da_zero == 0:
                                continue

                            if verifica_mese_coerente <= 0 or verifica_mese_coerente > 12:
                                continue
                                


                    
                    except Exception as e:
                        # print('Errore in conversione del valore "{}" a numerico: "{}"'.format(elements[1], e))

                        #se è vuoto aggiungo ad una lista di appoggio che servirà dopo per verificare che i parametri di compute_increments erano presenti nel file iniziale, anche se senza dati
                        if elements[1] == "":
                            anno_vuoto_pulito = elements[0].split('-')[0]
                            if anno_vuoto_pulito not in anni_vuoti:
                                anni_vuoti.append(anno_vuoto_pulito)
                        

                        
                        #continue utilizzato per saltare l'iterazione in cui non è possibile avere tipo di dato int, senza bloccare il codice
                        continue
                else: 
                    # print('Errore, pattern data errato')
                    continue

                anno_mese = elements[0].split('-')
                
                anno = int(anno_mese[0])
                mese = int(anno_mese[1])


                #siamo alla prima iterazione
                if count == 0:
                    anno_max = anno
                    mese_max = mese

                else:
                    if anno < anno_max:
                        raise ExamException("Errore: Non è ordinata: Anno \"{}\" è minore di Anno Massimo \"{}\"".format(anno, anno_max))

                    if anno == anno_max:
                        if mese < mese_max:
                            raise ExamException("Errore: Non è ordinata: Anno \"{}\" è uguale a Anno Massimo \"{}\", ma Mese \"{}\" è minore di Mese Massimo \"{}\"".format(anno, anno_max, mese, mese_max))
    
                        if mese == mese_max:
                            raise ExamException("Errore: Ripetizione: Anno è uguale: Anno \"{}\", Anno Massimo \"{}\" e anche il Mese \"{}\" è uguale a Mese Massimo \"{}\"".format(anno, anno_max, mese, mese_max))
    
                        if mese > mese_max:
                            mese_max = mese

                    if anno > anno_max:
                        anno_max = anno
                        mese_max = mese
                
                count+=1

                
                #lista da append a data, comprende solo la data e il numero ignorando la presenza di altri elementi nella riga, se trova i primi due, l'iterazione continua
                final_elements = []

                final_elements.append(elements[0])
                final_elements.append(elements[1])

                # Aggiungo alla lista gli elementi di questa linea
                data.append(final_elements)

        # Chiudo il file
        file.close()

        # Quando ho processato tutte le righe, ritorno i dati
        return data




#==============================
#  Funzione per il calcolo
#==============================

#in generale, ho considerato che se non ci sono misurazioni per un intero anno, lo rimuovo dal dizionario, in quanto in ogni caso va ignorato

def compute_increments(time_series, first_year, last_year):

    #verifico che i parametri first_year e last_year siano stringhe altrimenti alzo un'eccezione
    if not isinstance(first_year, str) or not isinstance(last_year, str):
        raise ExamException("Errore : Uno o più parametri passati in input come intervallo, non è una stringa.")

    #se i parametri inseriti sono il primo più grande dell'altro o se l'ultimo è più piccolo dell'altro li inverte, in modo da non bloccare il programma ma continuare lo stesso
    if int(first_year) > int(last_year) :
        tmp = first_year
        first_year = last_year
        last_year = tmp
    
    # Creazione del nuovo dizionario con le differenze tra le medie degli anni nell'intervallo
    intervalli_valori = {}

    #creazione un dizionario vuoto per contenere anni-media per anno
    anno_media = {}

    
    #dizionario di appoggio che ha come key l'anno e come valore il numero di passeggeri. Se la misurazione non esiste per un determinato mese non importa
    anno_valori = dizionario_anno_valori(time_series)


    if first_year not in anni_vuoti and first_year not in anno_valori.keys():
        raise ExamException("Errore : L'anno passato come parametro iniziale non è presente nel file. Ricorda che l'anno deve essere scritto con le cifre arabe (0-9) e senza lettere o simboli")

    if last_year not in anni_vuoti and last_year not in anno_valori.keys():
        raise ExamException("Errore : L'anno passato come parametro finale non è presente nel file. Ricorda che l'anno deve essere scritto con le cifre arabe (0-9) e senza lettere o simboli")

    #se uno dei due anni come parametri non ha dati e sono consecutivi
    if (last_year not in anno_valori.keys() or first_year not in anno_valori.keys()) and (int(last_year) - int(first_year) == 1):
        return []
    
    for anno, valori in anno_valori.items():
        
        # Calcolo della media dei valori per ogni anno, arrotondando ad un decimale tramite round
        media_valori_annua = round(sum(valori) / len(valori), 1)

        # Aggiunta della chiave e della media dei valori al nuovo dizionario
        anno_media[anno] = media_valori_annua

    
    #******************************
    #  Gestione casi speciali
    #******************************
    
    #Se l'anno inziale e l'anno finale coincidono stampo returno semplicemente l'anno desiderato col suo valore di media. Tuttavia se l'anno inserito è lo stesso ma non presenta alcuna misurazione, viene returnata una lista vuota
    if first_year == last_year:
        if first_year in anno_media.keys():
            return {first_year: anno_media[first_year]}
        else:
            return []
    
    #se l'anno iniziale e finale sono due anni che non presentano dati, ma sono presenti nel file, e hanno in mezzo un anno con dati presenti. ALlora stampo l'anno in mezzo. Esempio 1950 e 1952. Dove 1950 e 1952 non hanno dati, ma 1951 si, stampa quello (1951)
    if (first_year not in anno_media.keys() and first_year in anni_vuoti) and (last_year not in anno_media.keys() and last_year in anni_vuoti) and (int(last_year) - int(first_year) == 2):
        anno_in_mezzo = str(int(first_year) + 1)
        return {anno_in_mezzo: anno_media[anno_in_mezzo]}
        
        
    #ora prendo l'intervallo di anni voluto dal dizionario

    #anni è una lista che contiene tutte le chiavi (anni) del dizionario che contiene anni e media annua, dove non sono presenti anni che avevano valori nulli precedentemente
    anni = list(anno_media.keys())

    #usiamo len anni - 1 perchè avendo anni consecutivi (utilizzando il i + 1) rischiamo di andare oltre alla lunghezza della lista e avere errori se non facessimo in questo modo
    for i in range(len(anni) - 1):
        #anno iniziale e finale saranno due anni consecutivi
        anno_iniziale = anni[i]
        anno_finale = anni[i + 1]

        
        # Verifica se l'anno rientra nell'intervallo desiderato
        if first_year <= anno_iniziale <= last_year:
            # Crea la chiave dell'intervallo di anni (es. "1950-1951")
            intervallo_anni = "{}-{}".format(anno_iniziale, anno_finale)


            #se last year passato come parameteo non ha dati al suo interno, interrompe il ciclo. Casistica intervallo '49-'52, dati mancanti 1950 e 1952. Ideologicamente dovrebbe restituire 1949-1950 1950-1951 1951-1952. Ma dato che mancano quei due anni deve restituire 1949-1951 e basta. Questo controllo impedisce di memorizzare anche 1951-1953 che andrebbe oltre il limite alto imposto
            if(int(anno_finale) > int(last_year)):
                break
            
            
            # Calcola la differenza tra le medie degli anni consecutivi
            differenza_media = anno_media[anno_finale] - anno_media[anno_iniziale]

            # Aggiungi la chiave e la differenza al nuovo dizionario, arrotondata ad 1 decimale
            intervalli_valori[intervallo_anni] = round(differenza_media, 1)            
    return intervalli_valori




#==============================
#  Funzione ausiliaria per il semplificare il calcolo della media per ogni anno
#  Rende l'array di array
#==============================

def dizionario_anno_valori(time_series):

    #In questa funzione non è necessario tenere conto se un mese non presenta alcun dato, in quanto successivamente la media verrà calcolata in base ai dati ottenuti e non in base al numero del mese

    
    dizionario_risultante = {}

    #scorro i sotto-array nella lista di liste fornita da getData()
    for sotto_array in time_series:

        #time_series è del tipo [['1949-01', 112], ['1949-03', 132], ...
        #Per facilità di comprensione ho utilizzato una variabile d'appoggio chiamata valore che indica nell'esempi sopra 112, 132, ovvero i valori per ogni data (anno-mese)
        valore = sotto_array[1]
        
        # Estraiamo l'anno e il mese dalla data nel formato "anno-mese". Ovvero [['1949-01', /], ['1949-03', /], ...
        data = sotto_array[0]
        
        #Qua se data è "2024-02", allora data.split('-') restituirà la lista ['2024', '02']
        #In sintesi, questa singola linea di codice prende una stringa nel formato "anno-mese", la divide in due parti utilizzando il carattere '-', e converte queste parti in str, assegnandoli alle variabili anno e mese.
        anno, mese = map(str, data.split('-'))

        
        # Verifica se la chiave (anno) esiste nel dizionario
        if anno in dizionario_risultante:
            dizionario_risultante[anno].append(valore)
        else:
            # Se la chiave non esiste, creiamo una nuova lista con il dato
            dizionario_risultante[anno] = [valore]

    return dizionario_risultante



#==============================
#  Funzione ausilaria per verificare la correttezza del pattern data "YYYY-MM" tramite regex
#==============================

def verifica_pattern(data):

    #r, sta per 'raw', quindi i caratteri venogno presi letteralmente e non come escape (\), \d{4} \d indica cifre decimale [0-9], {4} il numero di cifre che si aspetta di quel tipo. - indica semplicemente il carattere trattino. Mentre ^ e $ indicano rispettivamente l'inizio e la fine della riga
    pattern = re.compile(r'^\d{4}-\d{2}$')
    if pattern.match(data):
        return True
    else:
        return False


# Esempio di utilizzo
# time_series_file = CSVTimeSeriesFile(name='dataProva.csv')
# time_series = time_series_file.get_data()
# # print(time_series)

# dizionario = compute_increments(time_series, '1960', '1950')
# print(dizionario)