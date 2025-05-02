def generate_email_text(filename,subject):
        parte_entre_parentesis = filename.split('(')[1].split(')')[0].strip()
        
        componentes = parte_entre_parentesis.split()
        
        dia_semana = componentes[0].lower()  # "viernes"
        
        fecha = componentes[1].split('-')
        dia = fecha[0]  # "02"
        mes_numero = fecha[1]  # "05"
        
        # Get career name (remaining words)
        carrera = ' '.join(componentes[2:]).lower()  # "ingeniería civil informática"
        
        # Spanish month names dictionary
        meses = {
            '01': 'enero', '02': 'febrero', '03': 'marzo', '04': 'abril',
            '05': 'mayo', '06': 'junio', '07': 'julio', '08': 'agosto',
            '09': 'septiembre', '10': 'octubre', '11': 'noviembre', '12': 'diciembre'
        }
        
        mes_nombre = meses.get(mes_numero, mes_numero)
        
        carrera = list(map(lambda x: x.capitalize(),carrera.split()))
        carrera = ' '.join(carrera) 
        return (f"Se envía adjunto el registro de asistencia para {subject} del {dia_semana} {dia} de "
                f"{mes_nombre} de la carrera de {carrera}.")
    

