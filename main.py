from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog
import sqlite3
import time
from PyQt5.QtCore import QThread, pyqtSignal
import os
import sys


# Carga el archivo .ui generado
Ui_MainWindow, QtBaseClass = uic.loadUiType("graf.ui")


    
class EjecucionCiclosThread(QThread):
    resultado_signal = pyqtSignal(float)  # Señal para enviar el resultado del contador de metros

    def __init__(self, Ltotal, Lmetros, ptotal):
        super().__init__()
        self.Ltotal = Ltotal
        self.Lmetros = Lmetros
        self.ptotal = ptotal

    def run(self):
        for i in range(self.Ltotal):
            time.sleep(3)  # Pequeña pausa para verificar la posición del tejido

            # Contador de metros
            resultado = i / self.Lmetros
            print('i',i) 
            print('mts',resultado)
            
            self.resultado_signal.emit(resultado)
            
            for p in range(self.ptotal):                
                time.sleep(0.5)
                print('p',p)

            

# Crea la clase principal de tu aplicación
class MiVentana(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.registrar.clicked.connect(self.registrar_clicked)
        self.iniciar.clicked.connect(self.iniciar_clicked)
        self.test.clicked.connect(self.test_clip)
        self.parar.clicked.connect(self.parar_clip)
        
        # Configurar el sensor
        self.ejecucion_thread = None
        
        
    def registrar_clicked(self):
        nmalla = self.nmalla.text()
        Pmetros = self.puntalto.text()
        Lmetros = self.lmetros.text()
        
        # Conectar a la base de datos
        conn = sqlite3.connect("db.db")
        cursor = conn.cursor()

        # Verificar si nmalla ya existe en la base de datos
        cursor.execute("SELECT * FROM tejido WHERE nmalla = ?", (nmalla,))
        result = cursor.fetchone()

        if result:
            # Actualizar los datos si nmalla ya existe
            cursor.execute("UPDATE tejido SET Pmetros = ?, Lmetros = ? WHERE nmalla = ?", (Pmetros, Lmetros, nmalla))
            print("Datos actualizados para nmalla:", nmalla)
        else:
            # Insertar nuevos datos si nmalla no existe
            cursor.execute("INSERT INTO tejido (nmalla, Pmetros, Lmetros) VALUES (?, ?, ?)", (nmalla, Pmetros, Lmetros))
            print("Datos insertados para nmalla:", nmalla)

        # Guardar los cambios en la base de datos
        conn.commit()

        # Cerrar la conexión a la base de datos
        conn.close()
        
        
    def actualizar_lcd_number(self, resultado):
        self.lcdNumber.display(resultado)
    
        
    def iniciar_clicked(self):
        nmalla = self.malla.text()
        
        # Conectar a la base de datos
        conn = sqlite3.connect("db.db")
        cursor = conn.cursor()

        # Verificar si nmalla existe en la base de datos
        cursor.execute("SELECT * FROM tejido WHERE nmalla = ?", (nmalla,))
        result = cursor.fetchone()
        
        if result:
            # Si nmalla existe, guardar los datos en variables
            Pmetros = result[1].replace(",", ".")
            Lmetros = result[2].replace(",", ".")
        
            # Reemplazar la coma por un punto en pmetros también
            pmetros = self.alto.text()
            lmetros = self.metros.text()
            pmetros = pmetros.replace (",", "." )
            lmetros = lmetros.replace (",", "." )
            try:
                # Intentar convertir los valores a números de punto flotante
                Pmetros = float(Pmetros)
                Lmetros = float(Lmetros)
                pmetros = float(pmetros)
                lmetros = float(lmetros)
                print("Pmetros:", pmetros)
                print("Lmetros:", lmetros)
                # Calculos para maquina
                ptotal = Pmetros * pmetros
                ptotal = int(ptotal)
                Ltotal = Lmetros * lmetros
                Ltotal = int(Ltotal)
                print("ptotal:", ptotal)
                print("Ltotal", Ltotal)
                
                self.ejecucion_thread = EjecucionCiclosThread(Ltotal, Lmetros, ptotal)
                self.ejecucion_thread.resultado_signal.connect(self.actualizar_lcd_number)
                self.ejecucion_thread.start()

                def actualizar_lcd_number(self, resultado):
                    self.lcdNumber.display(resultado)
                
                
            except ValueError:
                # Mostrar una alerta si la conversión falla
                QMessageBox.warning(self, "Alerta", "Los valores no son numéricos")

        else:
            # Mostrar una alerta si nmalla no existe en la base de datos
            QMessageBox.warning(self, "Alerta", f"La nmalla {nmalla} no existe en la base de datos")

        # Cerrar la conexión a la base de datos
        conn.close()
               

    def test_clip(self):
        cantidad_ciclos, ok = QInputDialog.getInt(None, "Cantidad de Ciclos", "Ingrese la cantidad de ciclos necesarios:")
        if ok:
            QMessageBox.information(None, "Cantidad de Ciclos", f"Cantidad de ciclos ingresada: {cantidad_ciclos}")
            time.sleep(10)
        else:
            QMessageBox.warning(None, "Cantidad de Ciclos", "No se ingresó una cantidad de ciclos.")
            
    def parar_clip(self):# Crear una instancia de QMessageBox
        alerta = QMessageBox()
        alerta.setIcon(QMessageBox.Question)
        alerta.setText("¿Deseas detener el proceso?")
        alerta.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        alerta.setDefaultButton(QMessageBox.No)

        # Mostrar la alerta y esperar por la respuesta
        respuesta = alerta.exec()

        # Si la respuesta es "Sí", reiniciar la aplicación
        if respuesta == QMessageBox.Yes:
            QtWidgets.qApp.quit()  # Cierra la aplicación actual

            # Reinicia la aplicación
            programa = sys.executable  # Ruta del intérprete de Python
            os.execl(programa, programa, *sys.argv)
        
        


# Crea una instancia de la ventana y muestra la interfaz gráfica
app = QtWidgets.QApplication([])
window = MiVentana()
window.show()
app.exec_()