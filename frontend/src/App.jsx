import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

function App() {
  const [anioSeleccionado, setAnioSeleccionado] = useState(2026)
  const [cantonReferencia, setCantonReferencia] = useState("TODOS")
  const [listaCantones, setListaCantones] = useState([])

  const [datosGrafico, setDatosGrafico] = useState([])
  const [datosTabla, setDatosTabla] = useState([])
  const [datosReferencia, setDatosReferencia] = useState([])
  const [totalAlertas, setTotalAlertas] = useState(0)
  const [totalRegistros, setTotalRegistros] = useState(0)
  const [cargando, setCargando] = useState(true)
  
  // Nuevo estado para mostrar que la IA está trabajando
  const [reentrenando, setReentrenando] = useState(false)

  const [form, setForm] = useState({
    codigo_acta: `DEMO-${Math.floor(Math.random() * 1000)}`,
    canton: 'Quito',
    parroquia: 'Iñaquito',
    empadronados: 300,
    votos_validos: 0,
    votos_blancos: 0,
    votos_nulos: 0
  })

  const cargarDatos = (anio, cantonRef) => {
    setCargando(true)
    fetch(`http://127.0.0.1:8000/api/actas/anomalias/?anio=${anio}&canton_ref=${cantonRef}`)
      .then(response => response.json())
      .then(data => {
        const actasAnomalas = data.anomalias || []
        
        setDatosTabla(actasAnomalas)
        setDatosReferencia(data.referencia || [])
        setListaCantones(data.cantones_disponibles || [])
        setTotalAlertas(data.total_alertas || 0)
        setTotalRegistros(data.total_registros || 0)
        
        const conteo = actasAnomalas.reduce((acc, acta) => {
          acc[acta.canton] = acc[acta.canton] || { canton: acta.canton, total_anomalias: 0 }
          acc[acta.canton].total_anomalias += 1
          return acc
        }, {})
        
        setDatosGrafico(Object.values(conteo).sort((a, b) => b.total_anomalias - a.total_anomalias))
        setCargando(false)
      })
      .catch(error => {
        console.error("Error al cargar los datos:", error)
        setCargando(false)
      })
  }

  useEffect(() => { 
    cargarDatos(anioSeleccionado, cantonReferencia) 
  }, [anioSeleccionado, cantonReferencia])

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })
  const handleAnioChange = (e) => {
    setAnioSeleccionado(e.target.value)
    setCantonReferencia("TODOS")
  }
  const handleCantonRefChange = (e) => setCantonReferencia(e.target.value)

  // --- LÓGICA DE EXPORTACIÓN A EXCEL (CSV) ---
  const exportarReporte = () => {
    if (datosTabla.length === 0) {
      alert("No hay anomalías para exportar en este periodo.");
      return;
    }
    
    // Armar el contenido del CSV
    const encabezados = "Codigo,Canton,Votos Validos,Empadronados,Riesgo IA (%)\n";
    const filas = datosTabla.map(acta => `${acta.codigo_acta},${acta.canton},${acta.votos_validos},${acta.empadronados},${acta.porcentaje_riesgo}`).join("\n");
    const contenidoCSV = encabezados + filas;
    
    // Descargar el archivo
    const blob = new Blob([contenidoCSV], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `Reporte_Fraudes_IA_${anioSeleccionado}.csv`;
    link.click();
  }

  // --- LÓGICA DEL PANEL DE CONTROL DE IA ---
  const reentrenarIA = async () => {
    if (!window.confirm("¿Estás seguro de reentrenar el Autoencoder? Esto forzará a la IA a re-evaluar todas las actas de la base de datos.")) return;
    
    setReentrenando(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/actas/reentrenar/', { method: 'POST' });
      const data = await res.json();
      
      if (data.status === 'success') {
        alert("✅ " + data.message);
        cargarDatos(anioSeleccionado, cantonReferencia); // Recargar la tabla con los nuevos porcentajes
      } else {
        alert("❌ Ocurrió un error en el backend: " + data.message);
      }
    } catch (error) {
      alert("❌ Error de conexión con el servidor.");
    }
    setReentrenando(false);
  }

  const simularActa = async (e) => {
    e.preventDefault()
    const res = await fetch('http://127.0.0.1:8000/api/actas/simular/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    const data = await res.json()
    
    if (data.es_anomala) {
      alert(`🚨 ¡ALERTA CRÍTICA!\nLa IA detectó fraude o inconsistencia severa en el acta.\nRiesgo calculado: ${data.riesgo}%`)
    } else {
      alert(`✅ Acta validada correctamente.\nPatrón normal detectado.\nRiesgo: ${data.riesgo}%`)
    }
    
    setForm({...form, codigo_acta: `DEMO-${Math.floor(Math.random() * 1000)}`})
    
    if (anioSeleccionado == 2026) {
      cargarDatos(2026, cantonReferencia)
    }
  }

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '30px', backgroundColor: '#f4f7f6', minHeight: '100vh' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '15px' }}>
        <div>
          <h1 style={{ color: '#2c3e50', margin: 0 }}>🚨 Auditoría Electoral IA</h1>
          
          <div style={{ marginTop: '10px', display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <label style={{ color: '#7f8c8d', fontWeight: 'bold' }}>Periodo de Análisis:</label>
            <select 
              value={anioSeleccionado} 
              onChange={handleAnioChange}
              style={{ padding: '5px 10px', borderRadius: '5px', border: '1px solid #bdc3c7', fontSize: '16px' }}
            >
              <option value="2026">2025/2026 (Simulación en Vivo)</option>
              <option value="2021">2021 (Histórico CNE)</option>
              <option value="2023">2023 (Asambleístas CNE)</option>
              <option value="2016">2016 (Histórico CNE)</option>
            </select>
            <span style={{color: '#95a5a6', fontSize: '14px', marginLeft: '10px'}}>
              (Base de datos: {totalRegistros} actas procesadas)
            </span>
          </div>
        </div>

        {/* PANEL DE CONTROL SUPERIOR */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <button 
            onClick={reentrenarIA} 
            disabled={reentrenando}
            style={{ backgroundColor: reentrenando ? '#95a5a6' : '#8e44ad', color: 'white', padding: '10px 15px', border: 'none', borderRadius: '5px', cursor: reentrenando ? 'not-allowed' : 'pointer', fontWeight: 'bold' }}
          >
            {reentrenando ? "⏳ Entrenando IA..." : "🧠 Reentrenar Red Neuronal"}
          </button>
          
          <div style={{ backgroundColor: '#e74c3c', color: 'white', padding: '10px 20px', borderRadius: '8px', fontWeight: 'bold', fontSize: '18px' }}>
            {totalAlertas} Alertas Críticas
          </div>
        </div>
      </header>

      <div style={{ backgroundColor: '#e8f6f3', padding: '15px', borderRadius: '8px', marginBottom: '20px', borderLeft: '5px solid #1abc9c' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', marginBottom: '10px' }}>
          <div>
            <h4 style={{ margin: 0, color: '#16a085' }}>📊 Datos Base (Referencia de Actas Normales)</h4>
            <p style={{ fontSize: '13px', color: '#7f8c8d', marginTop: '5px', marginBottom: 0 }}>
              Usa estos valores como guía. Ingresa números similares en el simulador para un acta "Normal", o altera drásticamente los Votos Válidos para generar una alerta.
            </p>
          </div>
          
          {listaCantones.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '10px' }}>
              <label style={{ fontWeight: 'bold', color: '#16a085', fontSize: '14px' }}>Filtrar guía por:</label>
              <select 
                value={cantonReferencia} 
                onChange={handleCantonRefChange}
                style={{ padding: '6px', borderRadius: '4px', border: '1px solid #1abc9c', outline: 'none', cursor: 'pointer' }}
              >
                <option value="TODOS">- Todos los Cantones -</option>
                {listaCantones.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          )}
        </div>

        {datosReferencia.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
              <thead>
                <tr style={{ backgroundColor: '#1abc9c', color: 'white', textAlign: 'left' }}>
                  <th style={{ padding: '8px' }}>Cantón</th>
                  <th style={{ padding: '8px' }}>Parroquia</th>
                  {/* NUEVA COLUMNA DE MESA */}
                  <th style={{ padding: '8px' }}>Mesa/Junta</th> 
                  <th style={{ padding: '8px' }}>Empadronados</th>
                  <th style={{ padding: '8px' }}>V. Válidos</th>
                  <th style={{ padding: '8px' }}>V. Blancos</th>
                  <th style={{ padding: '8px' }}>V. Nulos</th>
                </tr>
              </thead>
              <tbody>
                {datosReferencia.map((acta, idx) => (
                  <tr key={idx} style={{ backgroundColor: 'white', borderBottom: '1px solid #bdc3c7' }}>
                    <td style={{ padding: '8px', fontWeight: 'bold' }}>{acta.canton}</td>
                    <td style={{ padding: '8px' }}>{acta.parroquia}</td>
                    {/* NUEVO DATO DE MESA */}
                    <td style={{ padding: '8px', color: '#8e44ad', fontWeight: 'bold' }}>{acta.junta}</td>
                    <td style={{ padding: '8px' }}>{acta.empadronados}</td>
                    <td style={{ padding: '8px', color: '#27ae60', fontWeight: 'bold' }}>{acta.votos_validos}</td>
                    <td style={{ padding: '8px' }}>{acta.votos_blancos}</td>
                    <td style={{ padding: '8px' }}>{acta.votos_nulos}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ textAlign: 'center', color: '#7f8c8d', fontStyle: 'italic' }}>No hay datos de referencia para mostrar.</p>
        )}
      </div>
      
      {anioSeleccionado == 2026 && (
        <div style={{ backgroundColor: '#ecf0f1', padding: '20px', borderRadius: '8px', marginBottom: '20px', borderLeft: '5px solid #3498db' }}>
          <h3 style={{ marginTop: 0, color: '#2980b9' }}>🔬 Simulador de Ingreso en Tiempo Real</h3>
          <form onSubmit={simularActa} style={{ display: 'flex', gap: '15px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
            <div><label>Cantón</label><br/><input name="canton" value={form.canton} onChange={handleChange} style={{ padding: '8px' }}/></div>
            <div><label>Empadronados</label><br/><input type="number" name="empadronados" value={form.empadronados} onChange={handleChange} style={{ padding: '8px', width: '90px' }}/></div>
            <div><label>V. Válidos</label><br/><input type="number" name="votos_validos" value={form.votos_validos} onChange={handleChange} style={{ padding: '8px', width: '90px' }}/></div>
            <div><label>V. Blancos</label><br/><input type="number" name="votos_blancos" value={form.votos_blancos} onChange={handleChange} style={{ padding: '8px', width: '90px' }}/></div>
            <div><label>V. Nulos</label><br/><input type="number" name="votos_nulos" value={form.votos_nulos} onChange={handleChange} style={{ padding: '8px', width: '90px' }}/></div>
            <button type="submit" style={{ backgroundColor: '#2980b9', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
              Auditar Acta
            </button>
          </form>
        </div>
      )}

      {cargando ? ( <p style={{fontWeight: 'bold', color: '#2980b9'}}>Procesando red neuronal y extrayendo actas...</p> ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
          
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
            <h3 style={{ color: '#34495e', marginTop: 0 }}>Concentración de Anomalías por Cantón ({anioSeleccionado})</h3>
            <div style={{ width: '100%', height: 250 }}>
              <ResponsiveContainer>
                <BarChart data={datosGrafico} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="canton" />
                  <YAxis allowDecimals={false} />
                  <Tooltip cursor={{fill: '#f5f5f5'}} />
                  <Bar dataKey="total_anomalias" fill="#e74c3c" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
            
            {/* ENCABEZADO CON BOTÓN DE EXPORTACIÓN */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <h3 style={{ color: '#34495e', margin: 0 }}>Registro de Inconsistencias Críticas</h3>
              <button 
                onClick={exportarReporte}
                style={{ backgroundColor: '#27ae60', color: 'white', padding: '8px 15px', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' }}
              >
                📥 Exportar Reporte a Excel
              </button>
            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#2c3e50', color: 'white', textAlign: 'left' }}>
                  <th style={{ padding: '12px' }}>Código</th>
                  <th style={{ padding: '12px' }}>Cantón</th>
                  {/* NUEVA COLUMNA DE MESA */}
                  <th style={{ padding: '12px' }}>Mesa/Junta</th>
                  <th style={{ padding: '12px' }}>Votos Válidos</th>
                  <th style={{ padding: '12px' }}>Empadronados</th>
                  <th style={{ padding: '12px' }}>Riesgo IA</th>
                </tr>
              </thead>
              <tbody>
                {datosTabla.map((acta, index) => (
                  <tr key={acta.codigo_acta || index} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '12px', fontWeight: 'bold', color: '#2980b9' }}>{acta.codigo_acta}</td>
                    <td style={{ padding: '12px' }}>{acta.canton}</td>
                    {/* NUEVO DATO DE MESA */}
                    <td style={{ padding: '12px', color: '#8e44ad', fontWeight: 'bold' }}>{acta.junta}</td>
                    <td style={{ padding: '12px', color: '#c0392b', fontWeight: 'bold' }}>{acta.votos_validos}</td>
                    <td style={{ padding: '12px' }}>{acta.empadronados}</td>
                    <td style={{ padding: '12px' }}>
                      <span style={{ backgroundColor: '#ffeaa7', color: '#d35400', padding: '4px 8px', borderRadius: '12px', fontWeight: 'bold' }}>
                        {acta.porcentaje_riesgo}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {datosTabla.length === 0 && (
              <p style={{textAlign: 'center', color: '#7f8c8d', marginTop: '20px'}}>No se detectaron anomalías en este periodo.</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default App