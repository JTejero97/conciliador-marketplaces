import ReactDOM from 'react-dom/client';
import App from './App';

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
import React, { useState, useMemo } from 'react';
import { Sidebar } from './components/Sidebar';
import { DataPreview } from './components/DataPreview';
import { ProcessedTable } from './components/ProcessedTable';
import { KPIGrid } from './components/KPIGrid';
import { parseCSV } from './utils/csvParser';
import { processTransactions, calculateTotals } from './utils/dataProcessor';
import { CSVData, ProcessedRow } from './types';
import { CheckCircle2, FileText, Database } from 'lucide-react';

type Tab = 'report' | 'raw';

export default function App() {
  const [csvData, setCsvData] = useState<CSVData | null>(null);
  const [processedData, setProcessedData] = useState<ProcessedRow[] | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>('report');

  const handleFileSelect = async (file: File) => {
    setLoading(true);
    setError(null);
    setFileName(file.name);
    setCsvData(null);
    setProcessedData(null);
    
    try {
      const text = await file.text();
      const parsed = parseCSV(text);
      if (parsed.headers.length === 0) {
        throw new Error("El archivo CSV parece estar vacío o tiene un formato incorrecto.");
      }
      
      setCsvData(parsed);
      
      // Simular delay para UX
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const processed = processTransactions(parsed);
      setProcessedData(processed);
      setActiveTab('report'); // Reset to report tab on new file

    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido al procesar el archivo.");
      setCsvData(null);
      setProcessedData(null);
    } finally {
      setLoading(false);
    }
  };

  const totals = useMemo(() => {
    return processedData ? calculateTotals(processedData) : null;
  }, [processedData]);

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans">
      
      {/* Sidebar */}
      <Sidebar 
        onFileSelect={handleFileSelect} 
        loading={loading} 
        currentFile={fileName} 
      />

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Top Header */}
        <header className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between shrink-0">
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">
            Herramienta de Conciliación de Marketplaces
          </h1>
          {processedData && (
            <div className="flex items-center gap-2 text-sm font-medium text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-100 animate-fadeIn">
              <CheckCircle2 className="w-4 h-4" />
              Archivo procesado y cuadrado correctamente
            </div>
          )}
        </header>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto space-y-8">
            
            {error && (
              <div className="p-4 bg-red-50 text-red-700 rounded-xl border border-red-200 shadow-sm animate-fadeIn">
                <strong>Error:</strong> {error}
              </div>
            )}

            {!processedData && !loading && !error && (
              <div className="flex flex-col items-center justify-center h-96 text-center space-y-4 opacity-50">
                <div className="p-6 bg-slate-100 rounded-full">
                  <FileText className="w-12 h-12 text-slate-400" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-slate-600">Esperando archivo...</h2>
                  <p className="text-slate-500">Usa el panel lateral para cargar tu CSV de transacciones.</p>
                </div>
              </div>
            )}

            {processedData && totals && (
              <div className="animate-slideUp fade-in">
                {/* KPIs */}
                <KPIGrid totals={totals} />

                {/* Tabs */}
                <div className="mt-8">
                  <div className="border-b border-slate-200 mb-6">
                    <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                      <button
                        onClick={() => setActiveTab('report')}
                        className={`
                          group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm
                          ${activeTab === 'report'
                            ? 'border-brand-600 text-brand-600'
                            : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}
                        `}
                      >
                        <FileText className={`
                          -ml-0.5 mr-2 h-5 w-5
                          ${activeTab === 'report' ? 'text-brand-500' : 'text-slate-400 group-hover:text-slate-500'}
                        `} />
                      Reporte de Conciliación
                      </button>

                      <button
                        onClick={() => setActiveTab('raw')}
                        className={`
                          group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm
                          ${activeTab === 'raw'
                            ? 'border-brand-600 text-brand-600'
                            : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}
                        `}
                      >
                        <Database className={`
                          -ml-0.5 mr-2 h-5 w-5
                          ${activeTab === 'raw' ? 'text-brand-500' : 'text-slate-400 group-hover:text-slate-500'}
                        `} />
                         Datos en Bruto
                      </button>
                    </nav>
                  </div>

                  {/* Tab Content */}
                  <div className="min-h-[500px]">
                    {activeTab === 'report' ? (
                      <ProcessedTable data={processedData} totals={totals} />
                    ) : (
                      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                        <h3 className="text-lg font-semibold text-slate-800 mb-4">Vista Previa de Archivo Original</h3>
                        {csvData && <DataPreview data={csvData} />}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
import React from 'react';
import { CSVData } from '../types';

interface DataPreviewProps {
  data: CSVData;
}

export const DataPreview: React.FC<DataPreviewProps> = ({ data }) => {
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 shadow-sm">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-100">
          <tr>
            {data.headers.map((header, index) => (
              <th
                key={index}
                scope="col"
                className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider whitespace-nowrap"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-slate-200">
          {data.rows.map((row, rowIndex) => (
            <tr key={rowIndex} className="hover:bg-slate-50 transition-colors">
              {row.map((cell, cellIndex) => (
                <td
                  key={cellIndex}
                  className="px-6 py-4 whitespace-nowrap text-slate-700"
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
          {data.rows.length === 0 && (
            <tr>
              <td colSpan={data.headers.length} className="px-6 py-4 text-center text-slate-500 italic">
                No hay datos para mostrar
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};
import React, { useRef } from 'react';
import { UploadCloud, CheckCircle, Loader2 } from 'lucide-react';

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  loading: boolean;
  currentFile: string;
}

export const FileUploader: React.FC<FileUploaderProps> = ({ onFileSelect, loading, currentFile }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type === "text/csv" || file.name.endsWith('.csv')) {
        onFileSelect(file);
      } else {
        alert("Por favor sube un archivo CSV válido.");
      }
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div
      onClick={handleClick}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      className={`
        relative group cursor-pointer
        border-2 border-dashed rounded-lg p-6 transition-all duration-300 ease-in-out
        flex flex-col items-center justify-center text-center
        ${currentFile 
          ? 'border-brand-500 bg-brand-50/50' 
          : 'border-slate-600/50 bg-slate-800/30 hover:bg-slate-800/50 hover:border-brand-400'}
      `}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleChange}
        accept=".csv"
        className="hidden"
      />
      
      {loading ? (
        <div className="flex flex-col items-center text-brand-400">
          <Loader2 className="w-8 h-8 animate-spin mb-2" />
          <p className="text-sm font-medium">Procesando...</p>
        </div>
      ) : currentFile ? (
        <div className="flex flex-col items-center text-brand-400 animate-in fade-in zoom-in duration-300">
          <CheckCircle className="w-10 h-10 mb-2" />
          <p className="font-semibold text-sm break-all">{currentFile}</p>
          <p className="text-xs text-slate-400 mt-1">Clic para cambiar</p>
        </div>
      ) : (
        <>
          <div className="bg-slate-700/50 p-3 rounded-full mb-3 group-hover:scale-110 transition-transform duration-300">
            <UploadCloud className="w-6 h-6 text-brand-400" />
          </div>
          <p className="text-sm font-medium text-slate-200">
            Subir CSV
          </p>
          <p className="text-xs text-slate-400 mt-1">
            Arrastra o haz clic
          </p>
        </>
      )}
    </div>
  );
};
import React from 'react';
import { ProcessedRow } from '../types';
import { formatCurrency } from '../utils/dataProcessor';
import { Wallet, TrendingDown, Truck, ArrowRightCircle } from 'lucide-react';

interface KPIGridProps {
  totals: ProcessedRow;
}

export const KPIGrid: React.FC<KPIGridProps> = ({ totals }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Total Facturado */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
        <div className="flex justify-between items-start mb-2">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wide">Total Facturado</h4>
          <div className="p-2 bg-emerald-100 rounded-lg text-emerald-600">
            <Wallet className="w-5 h-5" />
          </div>
        </div>
        <div>
          <span className="text-2xl font-bold text-slate-800">{formatCurrency(totals.totalFactura)}</span>
          <p className="text-xs text-emerald-600 font-medium mt-1">+ Ingresos brutos</p>
        </div>
      </div>

      {/* Total Comisiones */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
        <div className="flex justify-between items-start mb-2">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wide">Total Comisiones</h4>
          <div className="p-2 bg-rose-100 rounded-lg text-rose-600">
            <TrendingDown className="w-5 h-5" />
          </div>
        </div>
        <div>
          <span className="text-2xl font-bold text-rose-700">{formatCurrency(totals.commission)}</span>
          <p className="text-xs text-rose-600 font-medium mt-1">Costes plataforma</p>
        </div>
      </div>

      {/* Total Envíos */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
        <div className="flex justify-between items-start mb-2">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wide">Total Envíos</h4>
          <div className="p-2 bg-amber-100 rounded-lg text-amber-600">
            <Truck className="w-5 h-5" />
          </div>
        </div>
        <div>
          <span className="text-2xl font-bold text-amber-700">{formatCurrency(totals.shippingFee)}</span>
          <p className="text-xs text-amber-600 font-medium mt-1">Logística</p>
        </div>
      </div>

      {/* TOTAL A INGRESAR */}
      <div className="bg-slate-900 p-5 rounded-xl border border-slate-800 shadow-lg flex flex-col justify-between relative overflow-hidden">
        <div className="absolute top-0 right-0 p-3 opacity-10">
          <ArrowRightCircle className="w-24 h-24 text-white" />
        </div>
        <div className="flex justify-between items-start mb-2 relative z-10">
          <h4 className="text-xs font-bold text-brand-200 uppercase tracking-wide">TOTAL A INGRESAR</h4>
          <div className="p-2 bg-brand-500/20 rounded-lg text-brand-300">
            <ArrowRightCircle className="w-5 h-5" />
          </div>
        </div>
        <div className="relative z-10">
          <span className="text-2xl font-bold text-white tracking-tight">{formatCurrency(totals.netTotal)}</span>
          <p className="text-xs text-brand-200 font-medium mt-1">Neto final conciliado</p>
        </div>
      </div>
    </div>
  );
};
                      import React from 'react';
import { ProcessedRow } from '../types';
import { formatCurrency, generateCSVContent } from '../utils/dataProcessor';
import { Download } from 'lucide-react';

interface ProcessedTableProps {
  data: ProcessedRow[];
  totals: ProcessedRow;
}

export const ProcessedTable: React.FC<ProcessedTableProps> = ({ data, totals }) => {
  
  const handleDownload = () => {
    const csvContent = generateCSVContent(data, totals);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'conciliacion_pagos_marketplaces.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-end mb-4">
        <button 
          onClick={handleDownload}
          className="flex items-center gap-2 px-6 py-3 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-all shadow-lg hover:shadow-brand-500/30 font-semibold text-sm transform active:scale-95 duration-200"
        >
          <Download className="w-5 h-5" />
          Descargar Reporte Conciliado (.csv)
        </button>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-200 shadow-sm bg-white">
        <table className="min-w-full divide-y divide-slate-200 text-sm whitespace-nowrap">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Tipo de Transacción</th>
              <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">ID de Pedido</th>
              <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Fecha</th>
              
              <th className="px-6 py-4 text-right text-xs font-bold text-slate-900 bg-slate-100 uppercase tracking-wider border-l border-slate-200">Total</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-emerald-700 bg-emerald-50/50 uppercase tracking-wider">Total Factura</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-rose-700 bg-rose-50/50 uppercase tracking-wider">Comisión Marketplace</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-amber-700 bg-amber-50/50 uppercase tracking-wider">Envío</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-slate-500 uppercase tracking-wider">Devolución</th>
              
              <th className="px-6 py-4 text-center text-xs font-bold text-indigo-700 bg-indigo-50/50 uppercase tracking-wider border-l border-slate-200">Retención (1%)</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-indigo-700 bg-indigo-50/50 uppercase tracking-wider">Imp. Retenido</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-white bg-slate-800 uppercase tracking-wider border-l border-slate-700">Total Neto</th>
              <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Plataforma</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-100">
            {data.map((row) => (
              <tr key={row.id} className="hover:bg-slate-50 transition-colors group">
                <td className="px-6 py-3 text-slate-600 text-xs">{row.transactionType}</td>
                <td className="px-6 py-3 text-slate-500 font-mono text-xs">{row.orderId}</td>
                <td className="px-6 py-3 text-slate-500 text-xs">{row.payoutDate}</td>
                
                <td className="px-6 py-3 text-right font-bold text-slate-700 bg-slate-50 group-hover:bg-white border-l border-slate-100 border-r">
                  {formatCurrency(row.total)}
                </td>
                
                <td className="px-6 py-3 text-right font-mono text-emerald-600 bg-emerald-50/10 group-hover:bg-emerald-50 text-xs">{formatCurrency(row.totalFactura)}</td>
                <td className="px-6 py-3 text-right font-mono text-rose-600 bg-rose-50/10 group-hover:bg-rose-50 text-xs">{formatCurrency(row.commission)}</td>
                <td className="px-6 py-3 text-right font-mono text-amber-600 bg-amber-50/10 group-hover:bg-amber-50 text-xs">{formatCurrency(row.shippingFee)}</td>
                <td className="px-6 py-3 text-right font-mono text-slate-400 text-xs">{formatCurrency(row.returnShippingFee)}</td>
                
                <td className="px-6 py-3 text-center font-bold text-indigo-600 bg-indigo-50/10 group-hover:bg-indigo-50 border-l border-slate-100 text-xs">{row.retentionFlag}</td>
                <td className="px-6 py-3 text-right font-mono text-indigo-600 bg-indigo-50/10 group-hover:bg-indigo-50 text-xs">{formatCurrency(row.retainedAmount)}</td>
                
                <td className="px-6 py-3 text-right font-bold text-slate-900 bg-slate-100 border-l border-slate-200 group-hover:bg-slate-200">
                  {formatCurrency(row.netTotal)}
                </td>
                
                <td className="px-6 py-3 text-slate-400 text-xs">{row.sellingPlatform}</td>
              </tr>
            ))}
          </tbody>
          <tfoot className="bg-slate-900 text-white font-bold text-sm shadow-inner relative z-10">
            <tr>
              <td className="px-6 py-5"></td> {/* Transaction Type */}
              <td className="px-6 py-5 whitespace-nowrap text-brand-400 tracking-wider">TOTAL BANCO</td>
              <td className="px-6 py-5"></td> {/* Date */}
              
              {/* Totals */}
              <td className="px-6 py-5 text-right border-l border-slate-700">{formatCurrency(totals.total)}</td>
              <td className="px-6 py-5 text-right text-emerald-400">{formatCurrency(totals.totalFactura)}</td>
              <td className="px-6 py-5 text-right text-rose-400">{formatCurrency(totals.commission)}</td>
              <td className="px-6 py-5 text-right text-amber-400">{formatCurrency(totals.shippingFee)}</td>
              <td className="px-6 py-5 text-right text-slate-400">{formatCurrency(totals.returnShippingFee)}</td>
              
              <td className="px-6 py-5 text-center border-l border-slate-700">-</td> {/* Retention Flag */}
              <td className="px-6 py-5 text-right text-indigo-300">{formatCurrency(totals.retainedAmount)}</td>
              <td className="px-6 py-5 text-right bg-black text-lg border-l border-slate-700 text-brand-300">{formatCurrency(totals.netTotal)}</td>
              
              <td className="px-6 py-5"></td> {/* Platform */}
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
};
                          import React from 'react';
import { FileUploader } from './FileUploader';
import { LayoutDashboard, FileSpreadsheet, Info } from 'lucide-react';

interface SidebarProps {
  onFileSelect: (file: File) => void;
  loading: boolean;
  currentFile: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ onFileSelect, loading, currentFile }) => {
  return (
    <aside className="w-80 bg-slate-900 text-white flex flex-col h-screen border-r border-slate-800 flex-shrink-0">
      {/* Brand */}
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center gap-3 mb-1">
          <div className="p-2 bg-brand-600 rounded-lg">
            <LayoutDashboard className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight">Tesorería</span>
        </div>
        <p className="text-slate-400 text-xs pl-1">Conciliador de Pagos v1.0</p>
      </div>

      {/* Main Actions */}
      <div className="p-6 flex-1 overflow-y-auto">
        <div className="mb-8">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
            <FileSpreadsheet className="w-4 h-4" />
            Cargar Datos
          </h3>
          <FileUploader 
            onFileSelect={onFileSelect} 
            loading={loading} 
            currentFile={currentFile} 
          />
        </div>

        <div className="mb-8">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Info className="w-4 h-4" />
            Instrucciones
          </h3>
          <div className="text-sm text-slate-400 space-y-3 leading-relaxed">
            <p>
              Esta herramienta transforma los <strong className="text-slate-200">Transaction Overview</strong> masivos en reportes contables.
            </p>
            <ul className="list-disc list-inside space-y-1 ml-1 marker:text-brand-500">
              <li>Sube el archivo CSV exportado.</li>
              <li>El sistema agrupará por Pedido y Tipo.</li>
              <li>Se calculan automáticamente las retenciones de la plataforma.</li>
              <li>Descarga el reporte final cuadrado.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 bg-slate-950 text-xs text-slate-500 text-center">
        &copy; {new Date().getFullYear()} Departamento Financiero
      </div>
    </aside>
  );
};
                    <!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Conciliador Marketplaces</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script>
      tailwind.config = {
        theme: {
          extend: {
            fontFamily: {
              sans: ['Inter', 'sans-serif'],
            },
            colors: {
              brand: {
                50: '#f0f9ff',
                100: '#e0f2fe',
                500: '#0ea5e9',
                600: '#0284c7',
                700: '#0369a1',
                900: '#0c4a6e',
              }
            }
          },
        },
      }
    </script>
  <script type="importmap">
{
  "imports": {
    "lucide-react": "https://esm.sh/lucide-react@^0.564.0",
    "react-dom/": "https://esm.sh/react-dom@^19.2.4/",
    "react/": "https://esm.sh/react@^19.2.4/",
    "react": "https://esm.sh/react@^19.2.4"
  }
}
</script>
</head>
  <body class="bg-slate-50 text-slate-900 antialiased">
    <div id="root"></div>
  </body>
</html>
           {
  "name": "Conciliador de Pagos",
  "description": "Herramienta para conciliar reportes de pagos de marketplaces.",
  "requestFramePermissions": []
}
           export interface CSVData {
  headers: string[];
  rows: string[][];
}

export interface ProcessedRow {
  id: string; // Unique key for React rendering
  orderItemId: string; // Used for grouping logic
  transactionType: string;
  orderId: string;
  payoutDate: string;
  sellingPlatform: string;
  
  // Financial fields
  totalFactura: number;
  commission: number;
  shippingFee: number;
  returnShippingFee: number;
  
  // Calculated fields
  total: number;
  retentionFlag: number; // 1% Retencion (1 or 0)
  retainedAmount: number;
  netTotal: number;
}
                    import { CSVData } from '../types';

export const parseCSV = (content: string, delimiter: string = ','): CSVData => {
  const lines = content.split(/\r\n|\n/).filter(line => line.trim() !== '');
  
  if (lines.length === 0) {
    return { headers: [], rows: [] };
  }

  // A simple parsing strategy. For production apps, robust libraries like PapaParse are recommended.
  // This handles basic commas.
  const parseLine = (line: string): string[] => {
    // Basic implementation that doesn't handle complex quoted strings with delimiters inside
    return line.split(delimiter).map(cell => cell.trim());
  };

  const headers = parseLine(lines[0]);
  // Get first 5 rows for preview
  const rows = lines.slice(1, 6).map(parseLine);

  return {
    headers,
    rows
  };
};
                     import { CSVData, ProcessedRow } from '../types';

export const processTransactions = (data: CSVData): ProcessedRow[] => {
  const { headers, rows } = data;

  // Helper to find column index by name (case insensitive)
  const getIndex = (name: string) => headers.findIndex(h => h.toLowerCase().trim() === name.toLowerCase());

  const idx = {
    orderItemId: getIndex('Order Item ID'),
    transactionType: getIndex('Transaction Type'),
    orderId: getIndex('Order ID'),
    payoutDate: getIndex('Payout / Refund Date'),
    sellingPlatform: getIndex('Selling platform'),
    amount: getIndex('Amount'),
    feeName: getIndex('Fee Name'),
  };

  // Validate critical columns exist
  if (idx.orderItemId === -1 || idx.transactionType === -1 || idx.amount === -1 || idx.feeName === -1) {
    console.warn("Faltan columnas críticas en el CSV.");
    return [];
  }

  // Pandas groupby replacement: Map<Key, AggregatedObject>
  const groups = new Map<string, ProcessedRow>();

  rows.forEach((row) => {
    if (row.length < headers.length) return;

    const orderItemId = row[idx.orderItemId] || '';
    const transactionType = row[idx.transactionType] || '';
    
    // Key based on: ['Order Item ID', 'Transaction Type']
    const key = `${orderItemId}|${transactionType}`;

    if (!groups.has(key)) {
      groups.set(key, {
        id: key,
        orderItemId,
        transactionType,
        orderId: idx.orderId !== -1 ? row[idx.orderId] : '',
        payoutDate: idx.payoutDate !== -1 ? row[idx.payoutDate] : '',
        sellingPlatform: idx.sellingPlatform !== -1 ? row[idx.sellingPlatform] : '',
        totalFactura: 0,
        commission: 0,
        shippingFee: 0,
        returnShippingFee: 0,
        total: 0,
        retentionFlag: 0,
        retainedAmount: 0,
        netTotal: 0
      });
    }

    const currentGroup = groups.get(key)!;
    const amountStr = idx.amount !== -1 ? row[idx.amount] : '0';
    const amount = parseFloat(amountStr) || 0;
    const feeName = idx.feeName !== -1 ? row[idx.feeName]?.trim() : '';

    if (['Item Price Credit', 'Reversal Item Price', 'Reversal Item Price Subsidy'].includes(feeName)) {
      currentGroup.totalFactura += amount;
    }

    if (['Commission', 'Reversal Commission'].includes(feeName)) {
      currentGroup.commission += amount;
    }

    if (feeName === 'Shipping Fee Paid by Seller') {
      currentGroup.shippingFee += amount;
    }
  });

  // Post-processing: Calculate Total, Retention, Net Total
  const processedRows = Array.from(groups.values()).map(row => {
    row.total = row.totalFactura + row.commission + row.shippingFee;

    const platform = row.sellingPlatform.toLowerCase().trim();
    const isMiravia = platform.includes('miravia');
    
    row.retentionFlag = isMiravia ? 1 : 0;
    row.retainedAmount = isMiravia ? row.total * 0.01 : 0;
    row.netTotal = row.total - row.retainedAmount;

    return row;
  });

  return processedRows;
};

export const calculateTotals = (rows: ProcessedRow[]): ProcessedRow => {
  return rows.reduce((acc, row) => ({
    ...acc,
    totalFactura: acc.totalFactura + row.totalFactura,
    commission: acc.commission + row.commission,
    shippingFee: acc.shippingFee + row.shippingFee,
    returnShippingFee: acc.returnShippingFee + row.returnShippingFee,
    total: acc.total + row.total,
    retainedAmount: acc.retainedAmount + row.retainedAmount,
    netTotal: acc.netTotal + row.netTotal,
    // Just summing retention flag for count if needed, or leave 0
    retentionFlag: 0 
  }), {
    id: 'TOTALS',
    orderItemId: '',
    transactionType: '',
    orderId: 'TOTAL BANCO', // Requirement: "TOTAL BANCO"
    payoutDate: '',
    sellingPlatform: '',
    totalFactura: 0,
    commission: 0,
    shippingFee: 0,
    returnShippingFee: 0,
    total: 0,
    retentionFlag: 0,
    retainedAmount: 0,
    netTotal: 0
  } as ProcessedRow);
};

export const generateCSVContent = (rows: ProcessedRow[], totals: ProcessedRow): string => {
  // Columns strictly requested
  const headers = [
    'Tipo de Transacción', 
    'ID de Pedido', 
    'Fecha de pago/reembolso',
    'Total', 
    'Total Factura', 
    'Comisión Marketplace', 
    'Gastos de envio', 
    'Paquete de devolución - Gastos de envío', 
    '1% Retencion', 
    'Importe Retenido', 
    'Total Neto', 
    'Plataforma de Venta'
  ];

  const escapeCsv = (val: string | number) => {
    if (val === null || val === undefined) return '';
    const str = String(val);
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  };

  const rowToString = (row: ProcessedRow) => [
    escapeCsv(row.transactionType),
    escapeCsv(row.orderId),
    escapeCsv(row.payoutDate),
    escapeCsv(row.total.toFixed(2)),
    escapeCsv(row.totalFactura.toFixed(2)),
    escapeCsv(row.commission.toFixed(2)),
    escapeCsv(row.shippingFee.toFixed(2)),
    escapeCsv(row.returnShippingFee.toFixed(2)),
    escapeCsv(row.retentionFlag),
    escapeCsv(row.retainedAmount.toFixed(2)),
    escapeCsv(row.netTotal.toFixed(2)),
    escapeCsv(row.sellingPlatform)
  ].join(',');

  const csvRows = rows.map(rowToString);
  const totalRow = rowToString(totals);

  return [headers.join(','), ...csvRows, totalRow].join('\n');
};

export const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(val);
};
   import { CSVData, ProcessedRow } from '../types';

export const processTransactions = (data: CSVData): ProcessedRow[] => {
  const { headers, rows } = data;

  // Helper to find column index by name (case insensitive)
  const getIndex = (name: string) => headers.findIndex(h => h.toLowerCase().trim() === name.toLowerCase());

  const idx = {
    orderItemId: getIndex('Order Item ID'),
    transactionType: getIndex('Transaction Type'),
    orderId: getIndex('Order ID'),
    payoutDate: getIndex('Payout / Refund Date'),
    sellingPlatform: getIndex('Selling platform'),
    amount: getIndex('Amount'),
    feeName: getIndex('Fee Name'),
  };

  // Validate critical columns exist
  if (idx.orderItemId === -1 || idx.transactionType === -1 || idx.amount === -1 || idx.feeName === -1) {
    console.warn("Faltan columnas críticas en el CSV.");
    return [];
  }

  // Pandas groupby replacement: Map<Key, AggregatedObject>
  const groups = new Map<string, ProcessedRow>();

  rows.forEach((row) => {
    if (row.length < headers.length) return;

    const orderItemId = row[idx.orderItemId] || '';
    const transactionType = row[idx.transactionType] || '';
    
    // Key based on: ['Order Item ID', 'Transaction Type']
    const key = `${orderItemId}|${transactionType}`;

    if (!groups.has(key)) {
      groups.set(key, {
        id: key,
        orderItemId,
        transactionType,
        orderId: idx.orderId !== -1 ? row[idx.orderId] : '',
        payoutDate: idx.payoutDate !== -1 ? row[idx.payoutDate] : '',
        sellingPlatform: idx.sellingPlatform !== -1 ? row[idx.sellingPlatform] : '',
        totalFactura: 0,
        commission: 0,
        shippingFee: 0,
        returnShippingFee: 0,
        total: 0,
        retentionFlag: 0,
        retainedAmount: 0,
        netTotal: 0
      });
    }

    const currentGroup = groups.get(key)!;
    const amountStr = idx.amount !== -1 ? row[idx.amount] : '0';
    const amount = parseFloat(amountStr) || 0;
    const feeName = idx.feeName !== -1 ? row[idx.feeName]?.trim() : '';

    if (['Item Price Credit', 'Reversal Item Price', 'Reversal Item Price Subsidy'].includes(feeName)) {
      currentGroup.totalFactura += amount;
    }

    if (['Commission', 'Reversal Commission'].includes(feeName)) {
      currentGroup.commission += amount;
    }

    if (feeName === 'Shipping Fee Paid by Seller') {
      currentGroup.shippingFee += amount;
    }
  });

  // Post-processing: Calculate Total, Retention, Net Total
  const processedRows = Array.from(groups.values()).map(row => {
    row.total = row.totalFactura + row.commission + row.shippingFee;

    const platform = row.sellingPlatform.toLowerCase().trim();
    const isMiravia = platform.includes('miravia');
    
    row.retentionFlag = isMiravia ? 1 : 0;
    row.retainedAmount = isMiravia ? row.total * 0.01 : 0;
    row.netTotal = row.total - row.retainedAmount;

    return row;
  });

  return processedRows;
};

export const calculateTotals = (rows: ProcessedRow[]): ProcessedRow => {
  return rows.reduce((acc, row) => ({
    ...acc,
    totalFactura: acc.totalFactura + row.totalFactura,
    commission: acc.commission + row.commission,
    shippingFee: acc.shippingFee + row.shippingFee,
    returnShippingFee: acc.returnShippingFee + row.returnShippingFee,
    total: acc.total + row.total,
    retainedAmount: acc.retainedAmount + row.retainedAmount,
    netTotal: acc.netTotal + row.netTotal,
    // Just summing retention flag for count if needed, or leave 0
    retentionFlag: 0 
  }), {
    id: 'TOTALS',
    orderItemId: '',
    transactionType: '',
    orderId: 'TOTAL BANCO', // Requirement: "TOTAL BANCO"
    payoutDate: '',
    sellingPlatform: '',
    totalFactura: 0,
    commission: 0,
    shippingFee: 0,
    returnShippingFee: 0,
    total: 0,
    retentionFlag: 0,
    retainedAmount: 0,
    netTotal: 0
  } as ProcessedRow);
};

export const generateCSVContent = (rows: ProcessedRow[], totals: ProcessedRow): string => {
  // Columns strictly requested
  const headers = [
    'Tipo de Transacción', 
    'ID de Pedido', 
    'Fecha de pago/reembolso',
    'Total', 
    'Total Factura', 
    'Comisión Marketplace', 
    'Gastos de envio', 
    'Paquete de devolución - Gastos de envío', 
    '1% Retencion', 
    'Importe Retenido', 
    'Total Neto', 
    'Plataforma de Venta'
  ];

  const escapeCsv = (val: string | number) => {
    if (val === null || val === undefined) return '';
    const str = String(val);
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  };

  const rowToString = (row: ProcessedRow) => [
    escapeCsv(row.transactionType),
    escapeCsv(row.orderId),
    escapeCsv(row.payoutDate),
    escapeCsv(row.total.toFixed(2)),
    escapeCsv(row.totalFactura.toFixed(2)),
    escapeCsv(row.commission.toFixed(2)),
    escapeCsv(row.shippingFee.toFixed(2)),
    escapeCsv(row.returnShippingFee.toFixed(2)),
    escapeCsv(row.retentionFlag),
    escapeCsv(row.retainedAmount.toFixed(2)),
    escapeCsv(row.netTotal.toFixed(2)),
    escapeCsv(row.sellingPlatform)
  ].join(',');

  const csvRows = rows.map(rowToString);
  const totalRow = rowToString(totals);

  return [headers.join(','), ...csvRows, totalRow].join('\n');
};

export const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(val);
};
import { CSVData } from '../types';

export const parseCSV = (content: string, delimiter: string = ','): CSVData => {
  const lines = content.split(/\r\n|\n/).filter(line => line.trim() !== '');
  
  if (lines.length === 0) {
    return { headers: [], rows: [] };
  }

  // A simple parsing strategy. For production apps, robust libraries like PapaParse are recommended.
  // This handles basic commas.
  const parseLine = (line: string): string[] => {
    // Basic implementation that doesn't handle complex quoted strings with delimiters inside
    return line.split(delimiter).map(cell => cell.trim());
  };

  const headers = parseLine(lines[0]);
  // Get first 5 rows for preview
  const rows = lines.slice(1, 6).map(parseLine);

  return {
    headers,
    rows
  };
};
