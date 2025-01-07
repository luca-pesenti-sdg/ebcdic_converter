      *================================================================*00000101
      *    NOME COPY     : MECCDW09                                     00000201
      *    AUTORE        : ROBERTA CELLI                                00000301
      *    DATA          : 14/05/04                                     00000401
      *    MMA           : 030885 ESTERO                                00000501
      *    DESCRIZIONE   : SCARICO MOVIMENTI PARTITE ESTERE PER MATRIX  00000601
      *    LUNGHEZZA     : 111                                          00000701
      *================================================================*00000801
       01  MECCDW09.                                                    00000902
             03  MECCDW09-KEY-PARTITA.                                  00001002
                 05  MECCDW09-IST           PIC  9(002).                00001102
                 05  MECCDW09-PARTITA       PIC  9(009).                00002002
            03  DETT              PIC   9.                              01250001
            03  CONTDAT           PIC  9(6).                            01260001
            03  DATA-SIST         PIC  9(6).                            01270001
            03  LTERM             PIC  X(8).                            01280001
            03  IMP               COMP-2.                               01290001
            03  CAM               COMP-2.                               01300001
            03  CTV               COMP-2.                               01310001
            03  SCADAT            PIC X(6).                             01320001
            03  SCADDAT           PIC X(6).                             01330001
            03  VALDAT            PIC X(6).                             01340001
            03  TAS               COMP-2.                               01350001
            03  REVTAS            PIC  9(6).                            01360001
            03  RIF-MACCH         PIC  9999999.                         01370001
            03  RIVAL             PIC   9.                              01380001
            03  USERID            PIC X(5).                             01390001
            03  VALDIS            PIC X(06).                            01400001
FABIO       03  DIV-ORIG          PIC 999.                              01420003
FABIO       03  FILLER            PIC X(01).                            01421003
