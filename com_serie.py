import time
import serial

#############################################
# Nota:
# Comentar esta linea si se utiliza el puerto serie
# con la FPGA
ser = serial.serial_for_url('loop://', timeout=1) ## en loop transmite localmente

#############################################
# Nota:
# Descomentar esta linea si se utiliza el puerto serie
# con la FPGA
#############################################
#ser = serial.Serial(
#    port     = '/dev/ttyUSB1', #COM3
#   baudrate = 9600,
#    parity   = serial.PARITY_NONE,
#   stopbits = serial.STOPBITS_ONE,
#    bytesize = serial.EIGHTBITS
#n b)


##################### FUNCIONES #######################
def send():
    while 1 :
        char_v = []
        data = input("ToSent: ")
        if data == 'exit':
            if ser.isOpen():
                ser.close()
            break
        else:
            # Arma el vector a transmitir
            for ptr in range(len(data)):
                char_v.append(data[ptr])
    #       print(char_v)
            
            for ptr in range(len(char_v)):
                ser.write(char_v[ptr].encode())
                #time.sleep(1)

            out = ''
            while ser.inWaiting() > 0:
                out += ser.read(1).decode()

#            if out != '':
#               print(">> " + out)
            return out
    


######################################################################################

ser.isOpen()
ser.timeout=None
ser.flushInput() # limpia buffer de entrada
ser.flushOutput() # limpia buffer de salida nm  

alpha=0.25
span=6
sps=8
rrc=True
while 1:
    print('Menu\n')
    print('1 - Factor de roll-off\n')
    print('2 - Span\n')
    print('3 - Sps\n')
    print('4 - Tipo de filtro\n')
 
    comando = send()
    match comando:
        case "1":
            print("Factor de roll-off\n")
            alpha = send();
        case "2":
            print("Span\n")
            span = send();
        case "3":
            print("Sps\n")
            sps = send();
        case "4":  # Este es el caso por defecto (default)
            print("Tipo de filtro\n")
            print("Inrese 1 para rrc o 0 para rc")
            tipo = send();
            if tipo == 1:
                rrc= True;
            else:
                rrc= False;
        case _:  # Este es el caso por defecto (default)
            print(f"Roll off: {alpha}, span: {span}, sps: {sps}, tipo: {rrc}")



        