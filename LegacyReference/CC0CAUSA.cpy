      **************************************************************            
      *   PARAMETRI DI RIDEFINIZIONE  DELLA PARTE DATI CONTENUTA   *            
      *   NELLA COPY UTCCTAB ALLO SCOPO DI PERSONALIZZARE I PARA-  *            
      *   METRI DELLA TABELLA CAUSALI.                             *            
      **************************************************************            
        15 CCAU-SEGM-OUT.                                                       
          20 FILLER                       PIC X(2).                             
          20 CCAU-KEY-OUT.                                                      
            25 CCAU-ID-OUT                PIC X(4).                             
            25 CCAU-KEY-SPEC-OUT.                                               
              30 CCAU-COD-CAU-OUT         PIC X(6).                             
              30 CCAU-RESTO-OUT           PIC X(10).                            
            25 CCAU-DATA-VALID-OUT        PIC X(6).                             
            25 CCAU-DATA-VALID-OUT-N REDEFINES CCAU-DATA-VALID-OUT              
                                              PIC 9(6).                         
          20 CCAU-DATI-OUT.                                                     
            25 CCAU-DESCR                 PIC X(24).                            
970765      25 CCAU-CAU-ABI-CBI           PIC XX.                               
970765      25 FILLER                     PIC X(4).                             
970765      25 CCAU-CAU-ABI-ATM           PIC XX.                               
            25 CCAU-COD-CAU-STOR.                                               
              30 CCAU-ABI-STOR            PIC XX.                               
              30 CCAU-STCAU-STOR          PIC X(4).                             
            25 CCAU-COD-CAU-SPESE.                                              
               30 CCAU-ABI-SPESE          PIC XX.                               
               30 CCAU-STCAU-SPESE        PIC X(4).                             
            25 CCAU-SEGNO                 PIC X.                                
               88 CCAU-ADDEB                  VALUE 'D'.                        
               88 CCAU-ACCAU                  VALUE 'A'.                        
            25 CCAU-FLAG-COMP             PIC X.                                
               88 CCAU-NO-COMP                VALUE '0'.                        
               88 CCAU-COMP                   VALUE '1'.                        
            25 CCAU-FLAG-EC               PIC X.                                
               88 CCAU-NO-EC                  VALUE '0'.                        
               88 CCAU-EC                     VALUE '1'.                        
            25 CCAU-FLAG-VALID-CC         PIC X.                                
               88 CCAU-NO-VALID-CC            VALUE '0'.                        
               88 CCAU-VALID-CC               VALUE '1'.                        
            25 CCAU-FLAG-VALID-DR         PIC X.                                
               88 CCAU-NO-VALID-DR            VALUE '0'.                        
               88 CCAU-VALID-DR               VALUE '1'.                        
            25 CCAU-FLAG-VALID-ANT        PIC X.                                
               88 CCAU-NO-VALID-ANT           VALUE '0'.                        
               88 CCAU-VALID-ANT              VALUE '1'.                        
            25 CCAU-FLAG-VALID-SOFF       PIC X.                                
               88 CCAU-NO-VALID-SOFF          VALUE '0'.                        
               88 CCAU-VALID-SOFF             VALUE '1'.                        
            25 FILLER                     PIC X(6).                             
            25 CCAU-FLAG-ACCENTR          PIC X.                                
               88 CCAU-SOLO-ACCENTR           VALUE '2'.                        
               88 CCAU-SPOR-ACCENTR           VALUE '1'.                        
               88 CCAU-SOLO-SPOR              VALUE '0'.                        
            25 CCAU-FLAG-OPER-GEN         PIC X.                                
               88 CCAU-NO-OPER-GEN            VALUE '0'.                        
               88 CCAU-SI-OPER-GEN            VALUE '1' '2' '3'.                
               88 CCAU-OPER-GEN-NO-EST        VALUE '1'.                        
               88 CCAU-OPER-GEN-SI-EST        VALUE '2'.                        
               88 CCAU-OPER-GEN-ANCHE-EST     VALUE '3'.                        
            25 CCAU-FLAG-PART-PREN        PIC X.                                
               88 CCAU-NO-PART-PREN           VALUE '9'.                        
               88 CCAU-PART-PREN              VALUE '0' '1'.                    
            25 CCAU-FLAG-PART-ANN         PIC X.                                
               88 CCAU-NO-PART-ANN            VALUE '9'.                        
               88 CCAU-PART-ANN               VALUE '0' '1'.                    
            25 FILLER                     PIC XX.                               
            25 CCAU-SEGNO-VAL-MIN         PIC X.                                
               88 CCAU-POS-VAL-MIN            VALUE '+'.                        
               88 CCAU-NEG-VAL-MIN            VALUE '-'.                        
            25 CCAU-GG-VAL-MIN            PIC 9(3).                             
            25 CCAU-SEGNO-VAL-MAX         PIC X.                                
               88 CCAU-POS-VAL-MAX            VALUE '+'.                        
               88 CCAU-NEG-VAL-MAX            VALUE '-'.                        
            25 CCAU-GG-VAL-MAX            PIC 9(3).                             
            25 CCAU-FLAG-CNTR-VAL         PIC X.                                
               88 CCAU-MAX-FAV-CLI            VALUE 'F'.                        
               88 CCAU-MAX                    VALUE 'M'.                        
            25 CCAU-COD-RAGGR-2FIDI       PIC XX.                               
            25 CCAU-COD-RAGGR-STC         PIC XX.                               
            25 FILLER                     PIC X(20).                            
            25 FILLER                     PIC X(20).                            
            25 FILLER                     PIC X(20).                            
            25 FILLER                     PIC X(20).                            
            25 CCAU-DATI-DATA-FINANZIARIA.                                      
               30 CCAU-FLAG-DATA-FIN-TIPO-GG PIC X.                             
                  88 CCAU-LAV-FIN-TIPO-GG        VALUE 'L'.                     
                  88 CCAU-CAL-FIN-TIPO-GG        VALUE 'C'.                     
               30 CCAU-FLAG-DATA-FIN-RIFER   PIC X.                             
                  88 CCAU-OPE-DATA-FIN           VALUE 'O'.                     
                  88 CCAU-VAL-DATA-FIN           VALUE 'V'.                     
               30 CCAU-FLAG-DATA-FIN-SEGNO   PIC X.                             
                  88 CCAU-SOM-DATA-FIN           VALUE '+'.                     
                  88 CCAU-SOT-DATA-FIN           VALUE '-'.                     
               30 CCAU-DATA-FIN-NUM-GG       PIC 9(3).                          
            25 CCAU-DATI-DATA-PROCESSO.                                         
               30 CCAU-FLAG-DATA-PRO-TIPO-GG PIC X.                             
                  88 CCAU-LAV-PRO-TIPO-GG        VALUE 'L'.                     
               30 CCAU-FLAG-DATA-PRO-RIFER   PIC X.                             
                  88 CCAU-OPE-DATA-PRO           VALUE 'O'.                     
               30 CCAU-FLAG-DATA-PRO-SEGNO   PIC X.                             
                  88 CCAU-SOM-DATA-PRO           VALUE '+'.                     
                  88 CCAU-SOT-DATA-PRO           VALUE '-'.                     
               30 CCAU-DATA-PRO-NUM-GG       PIC 9(3).                          
            25 CCAU-DATI-DATA-PASSAGGIO.                                        
               30 CCAU-FLAG-DATA-PAS-TIPO-GG PIC X.                             
                  88 CCAU-LAV-PAS-TIPO-GG        VALUE 'L'.                     
                  88 CCAU-CAL-PAS-TIPO-GG        VALUE 'C'.                     
               30 CCAU-FLAG-DATA-PAS-RIFER   PIC X.                             
                  88 CCAU-OPE-DATA-PAS           VALUE 'O'.                     
                  88 CCAU-PRO-DATA-PAS           VALUE 'P'.                     
                  88 CCAU-FIN-DATA-PAS           VALUE 'F'.                     
                  88 CCAU-VAL-DATA-PAS           VALUE 'V'.                     
               30 CCAU-FLAG-DATA-PAS-SEGNO   PIC X.                             
                  88 CCAU-SOM-DATA-PAS           VALUE '+'.                     
                  88 CCAU-SOT-DATA-PAS           VALUE '-'.                     
               30    CCAU-DATA-PAS-NUM-GG    PIC 9(03).                         
            25 FILLER                     PIC X(17).                            
            25 CCAU-COD-IVA               PIC X(3).                             
            25 CCAU-COD-OPER-IVA          PIC 9(2).                             
            25 CCAU-FLAG-FATT             PIC X.                                
            25 CCAU-FLAG-CENTR-RISCHI     PIC X.                                
            25 CCAU-COD-TRANS-ACCEN       PIC X(4).                             
            25 CCAU-TIPO-TRATT-ACCEN      PIC X.                                
            25 CCAU-FLAG-ANTIMAFIA        PIC X.                                
            25 CCAU-CAUS-ANTIRICICL       PIC X(4).                             
            25 CCAU-VOCE-FAM-BIL          PIC 9(2).                             
            25 CCAU-FLAG-COFIMEDIT        PIC X.                                
               88 CCAU-CAUSALE-NON-TIT        VALUE '0'.                        
               88 CCAU-CAUSALE-TIT            VALUE '1'.                        
               88 CCAU-CAUSALE-TIT-ELIM       VALUE '9'.                        
920354      25 CCAU-FLAG-DESC-EC          PIC X(2).                             
920354         88 CCAU-NO-DESC-AGG-EC         VALUE 'NO'.                       
920354      25 CCAU-FLAG-CT-DESC-EC       PIC X(2).                             
920354         88 CCAU-NO-CT-DESC-EC          VALUE 'NO'.                       
920354      25 CCAU-FLAG-DECOD-CAUS       PIC X.                                
920354         88 CCAU-NO-DECOD-CAUS          VALUE 'N'.                        
            25 CCAU-FLAG-COMMERC          PIC X.                                
000765      25 CCAU-CAU-UIC               PIC X(4).                             
000765      25 CCAU-FLU                   PIC X(6).                             
000905      25 CCAU-VALAN-VALUTE-ANOMAL.                                        
000905         30 CCAU-VALAN-GG-ANTERG    PIC 9(3).                             
000905         30 CCAU-VALAN-GG-POSTERG   PIC 9(3).                             
000905         30 CCAU-VALAN-LIM-IMP      PIC 9(13)V9(2) COMP-3.                
990908      25 CCAU-FLAG-OK-DESC-EC       PIC X.                                
990908         88 CCAU-FLAG-OK-DESC-EC-SI     VALUE 'S'.                        
990908         88 CCAU-FLAG-OK-DESC-EC-NO     VALUE 'N'.                        
            25 CCAU-BLOCCO-ANAG-ACC       PIC X.                                
941188      25 CCAU-OPER-INIZ-CLI         PIC X.                                
VIRDUE      25 CCAU-CANALE-ACC            PIC X(3).                             
040087      25 CCAU-FLAG-OK-TERZA-RIGA    PIC X.                                
CASMAN      25 CCAU-CAU-SWIFT             PIC X(3).                             
051432      25 CCAU-CAUS-ANTR-CAS         PIC X(2).                             
051432      25 CCAU-SEGNO-CAUS-ANTR-CAS   PIC X.                                
051432      25 CCAU-CAUS-ACCBAN           PIC X(3).                             
051432      25 CCAU-SEGNO-CAUS-ACCBAN     PIC X.                                
071527      25 CCAU-CAUS-MOV-CONDOR       PIC X.                                
100413      25 CCAU-COD-RAG-PSD           PIC XX.                               
120113      25 CCAU-FLAG-APPLIC-STC       PIC X.                                
120113         88 CCAU-FLAG-APPLIC-STC-SEMPRE VALUE 'S'.                        
120113         88 CCAU-FLAG-APPLIC-STC-MAI    VALUE 'M'.                        
120113         88 CCAU-FLAG-APPLIC-STC-LIBERO VALUE 'L'.                        
CIV         25 CCAU-FLAG-APPLIC-CIV       PIC X.                                
CIV            88 CCAU-FLAG-APPLIC-CIV-SI     VALUE 'S'.                        
CIV            88 CCAU-FLAG-APPLIC-CIV-NO     VALUE 'N'.                        
CONBO       25 CCAU-FLAG-MOVBOL-SCU       PIC X.                                
CONBO          88 CCAU-FLAG-MOVBOL-SCU-N      VALUE 'N'.                        
CONBO          88 CCAU-FLAG-MOVBOL-SCU-E      VALUE 'E'.                        
CONBO          88 CCAU-FLAG-MOVBOL-SCU-V      VALUE 'V'.                        
CONBO          88 CCAU-FLAG-MOVBOL-SCU-S      VALUE 'S'.                        
            25 FILLER                     PIC X(06).                            
