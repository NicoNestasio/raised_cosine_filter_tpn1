## TP N1 Facundo Nestasio - Python Lab
import time
import serial
import numpy as np
import matplotlib.pyplot as plt


################################################
alpha=1
span=10
sps=10
rrc=True

#######################################

# ---- PUERTO SERIE

########################################
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
    
class RaisedCosineFilter:
    def __init__(self, alpha, span, sps, rrc):
        """
        Filtro de coseno realzado o raíz de coseno realzado.
        
        Parámetros:
        - alpha: Factor de roll-off (0 <= alpha <= 1)
        - span: Duración total del filtro en símbolos
        - sps: Muestras por símbolo
        - rrc: Si True, genera raíz de coseno realzado; si False, coseno realzado
        """
        self.alpha = alpha
        self.span = span
        self.sps = sps
        self.rrc = rrc
        self.taps = self._generate_filter()

    def _generate_filter(self):

        T = 1  # Duración del símbolo (normalizado)
        N = self.span * self.sps
        t = np.arange(-N//2, N//2 + 1) / self.sps

        if self.rrc:
            # Filtro Root Raised Cosine
            h = np.zeros_like(t)
            for i in range(len(t)):
                ti = t[i]
                if ti == 0.0:
                    h[i] = 1.0 - self.alpha + (4 * self.alpha / np.pi)
                elif abs(ti) == T / (4 * self.alpha):
                    h[i] = (self.alpha / np.sqrt(2)) * (
                        ((1 + 2/np.pi) * (np.sin(np.pi/(4*self.alpha)))) +
                        ((1 - 2/np.pi) * (np.cos(np.pi/(4*self.alpha))))
                    )
                else:
                    h[i] = (np.sin(np.pi * ti * (1 - self.alpha) / T) +
                            4 * self.alpha * ti / T *
                            np.cos(np.pi * ti * (1 + self.alpha) / T)) / \
                           (np.pi * ti * (1 - (4 * self.alpha * ti / T) ** 2))
        else:
            # Filtro Raised Cosine clásico
            h = np.zeros_like(t)
            for i in range(len(t)):
                ti = t[i]
                if ti == 0.0:
                    h[i] = 1.0
                elif abs(ti) == T / (2 * self.alpha):
                    h[i] = (np.pi / 4) * np.sinc(1 / (2 * self.alpha))
                else:
                    h[i] = np.sinc(ti / T) * \
                           np.cos(np.pi * self.alpha * ti / T) / \
                           (1 - (2 * self.alpha * ti / T) ** 2)

        return h

def plot_comparativa(lista_de_filtros):

    plt.figure(figsize=(10, 8), dpi=100)
    colores = ['c', 'm', 'y']


    plt.subplot(2, 1, 1)
    for idx, f_obj in enumerate(lista_de_filtros):
        t = np.arange(-len(f_obj.taps)//2, len(f_obj.taps)//2 + 1) / f_obj.sps
        t = t[:len(f_obj.taps)]
        
        tipo_lbl = "RRC" if f_obj.rrc else "RC"
        leyenda_txt = f"Filtro {idx+1}: {tipo_lbl} (alpha={f_obj.alpha})"
        
        plt.stem(t, f_obj.taps, linefmt=colores[idx]+'-', markerfmt=colores[idx]+'o', 
                 basefmt='k-', label=leyenda_txt)
        
    plt.title("Raised Cosine Filter (Time Domain)")
    plt.xlabel("Time [symbol periods]")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend()

    plt.subplot(2, 1, 2)
    for idx, f_obj in enumerate(lista_de_filtros):
        H = np.fft.fftshift(np.fft.fft(f_obj.taps, 256))
        f = np.linspace(-0.5, 0.5, len(H), endpoint=False)
        
        # 1. Obtenemos la magnitud absoluta (escala lineal)
        magnitud_lineal = np.abs(H)
        
        # 2. NORMALIZACIÓN: Dividimos por el máximo para que el techo sea 1.0
        magnitud_normalizada = magnitud_lineal / np.max(magnitud_lineal)
        
        tipo_lbl = "RRC" if f_obj.rrc else "RC"
        leyenda_txt = f"Filtro {idx+1}: {tipo_lbl} (alpha={f_obj.alpha})"
        
        markerline, stemlines, baseline = plt.stem(f, magnitud_normalizada, linefmt=colores[idx]+'-', 
                                                   markerfmt=' ', basefmt='k-', bottom=0, label=leyenda_txt)
        plt.setp(stemlines, alpha=0.5)
        
    plt.title("Raised Cosine Filter (Frequency Domain)")
    plt.xlabel("Normalized Frequency [×π rad/sample]")
    plt.ylabel("Magnitude [dB]")
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.show()

    def get_coefficients(self):
        return self.taps

######################################################################################

ser.isOpen()
ser.timeout=None
ser.flushInput() # limpia buffer de entrada
ser.flushOutput() # limpia buffer de salida nm  
#######################################
# ---- FILTRO
#######################################

lista_filtros = []
max_filtros = 3

for i in range(max_filtros):
    print(f"\n=========================================")
    print(f" CONFIGURACIÓN DEL FILTRO N°{i+1} DE {max_filtros}")
    print(f"=========================================")
    
    alpha = 0.25
    span = 6
    sps = 8
    rrc = False

    while 1:
        tipo_actual = "RRC" if rrc else "RC"

        print(f'1 - Factor de roll-off [Actual: {alpha}]\n')
        print(f'2 - Span [Actual: {span}]\n')
        print(f'3 - Sps [Actual: {sps}]\n')
        print(f'4 - Tipo de filtro [Actual: {tipo_actual}]\n')
        print(f'Cualquier otra tecla - Confirmar filtro {i+1} y continuar\n')
     
        comando = send()
        match comando:
            case "1":
                print("Factor de roll-off\n")
                while True:
                    print("Ingrese un valor entre 0 y 1 (ej: 0.25):")
                    valor_ingresado = float(send())
                    if 0.0 <= valor_ingresado <= 1.0:
                        alpha = valor_ingresado
                        print(f"Roll-off aceptado: {alpha}\n")
                        break
                    else:
                        print("Error: El factor debe estar entre 0 y 1. Intente de nuevo.\n")               
            case "2":
                print("Span\n")
                span = int(send())
            case "3":
                print("Muestras por símbolo (Sps)\n")
                sps = int(send())
            case "4":  
                print("Tipo de filtro\n")
                print("Ingrese 1 para rrc o 0 para rc")
                tipo = send()
                if tipo == "1":
                    rrc = True
                else:
                    rrc = False
            case _:  
                print(f"Filtro {i+1} guardado -> Roll off: {alpha}, span: {span}, sps: {sps}, tipo: {rrc}\n")
                break

    filtro_objeto = RaisedCosineFilter(alpha, span, sps, rrc)
    lista_filtros.append(filtro_objeto)

plot_comparativa(lista_filtros)