"""Pantalla principal estilizada para consulta de productos en Northwind."""

import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from configuracion.db import buscar_productos


class VentanaConsultaProductos(tk.Tk):
    """Interfaz con estilos personalizados, filtros y grilla Treeview."""

    def __init__(self):
        super().__init__()
        self.title("Northwind - Consulta de Productos")
        self.geometry("900x500")
        self.configure(bg="#F4F6F9")

        self._configurar_estilos()
        self._crear_encabezado()
        self._crear_buscador()
        self._crear_grilla()
        self._buscar()

    def _configurar_estilos(self):
        style = ttk.Style(self)
        # 'clam' permite personalizar colores de botones y encabezados en Windows
        style.theme_use("clam")

        # Tipografía y fondos generales
        style.configure("TFrame", background="#F4F6F9")
        style.configure("TLabel", background="#F4F6F9", foreground="#1E293B", font=("Segoe UI", 10))
        style.configure("TLabelframe", background="#F4F6F9", bordercolor="#CBD5E1")
        style.configure(
            "TLabelframe.Label",
            background="#F4F6F9",
            foreground="#0F172A",
            font=("Segoe UI", 10, "bold"),
        )

        # Cajas de texto
        style.configure("TEntry", fieldbackground="#FFFFFF", padding=5, font=("Segoe UI", 10))

        # Botón principal (Buscar)
        style.configure(
            "Primario.TButton",
            background="#2563EB",
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 5),
            borderwidth=0,
        )
        style.map("Primario.TButton", background=[("active", "#1D4ED8")])

        # Botón secundario (Limpiar)
        style.configure(
            "Secundario.TButton",
            background="#E2E8F0",
            foreground="#334155",
            font=("Segoe UI", 10),
            padding=(10, 5),
            borderwidth=0,
        )
        style.map("Secundario.TButton", background=[("active", "#CBD5E1")])

        # Estilo de la grilla (Treeview)
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#1E293B",
            rowheight=28,
            fieldbackground="#FFFFFF",
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background="#1E293B",
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            padding=6,
            relief="flat",
        )
        style.map("Treeview.Heading", background=[("active", "#334155")])
        style.map(
            "Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", "#1E3A8A")],
        )

    def _crear_encabezado(self):
        header = tk.Frame(self, bg="#1E293B", height=50)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Gestión de Productos — Northwind",
            bg="#1E293B",
            fg="#FFFFFF",
            font=("Segoe UI", 13, "bold"),
            padx=15,
            pady=10,
        ).pack(side="left")

    def _crear_buscador(self):
        frame_filtros = ttk.LabelFrame(self, text="Filtros de búsqueda", padding=12)
        frame_filtros.pack(fill="x", padx=15, pady=12)

        ttk.Label(frame_filtros, text="Producto:").grid(row=0, column=0, padx=5, sticky="w")
        self.ent_producto = ttk.Entry(frame_filtros, width=25)
        self.ent_producto.grid(row=0, column=1, padx=5)
        self.ent_producto.bind("<Return>", lambda _e: self._buscar())

        ttk.Label(frame_filtros, text="Categoría:").grid(row=0, column=2, padx=(15, 5), sticky="w")
        self.ent_categoria = ttk.Entry(frame_filtros, width=25)
        self.ent_categoria.grid(row=0, column=3, padx=5)
        self.ent_categoria.bind("<Return>", lambda _e: self._buscar())

        ttk.Button(
            frame_filtros, text="Buscar", style="Primario.TButton", command=self._buscar
        ).grid(row=0, column=4, padx=(15, 5))

        ttk.Button(
            frame_filtros, text="Limpiar", style="Secundario.TButton", command=self._limpiar
        ).grid(row=0, column=5, padx=5)

    def _crear_grilla(self):
        frame_tabla = ttk.Frame(self, padding=(15, 0, 15, 15))
        frame_tabla.pack(fill="both", expand=True)

        columnas = ("id", "producto", "categoria", "proveedor", "precio", "stock")
        self.grilla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

        # Colores alternados para las filas (efecto cebra)
        self.grilla.tag_configure("par", background="#FFFFFF")
        self.grilla.tag_configure("impar", background="#F8FAFC")

        encabezados = [
            ("id", "ID", 50, "center"),
            ("producto", "Producto", 230, "w"),
            ("categoria", "Categoría", 140, "w"),
            ("proveedor", "Proveedor", 210, "w"),
            ("precio", "Precio Unit.", 95, "e"),
            ("stock", "Stock", 70, "center"),
        ]

        for col, texto, ancho, alineacion in encabezados:
            self.grilla.heading(col, text=texto, anchor=alineacion)
            self.grilla.column(col, width=ancho, anchor=alineacion)

        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.grilla.yview)
        self.grilla.configure(yscrollcommand=scroll.set)

        self.grilla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _buscar(self):
        for item in self.grilla.get_children():
            self.grilla.delete(item)

        prod = self.ent_producto.get()
        cat = self.ent_categoria.get()

        try:
            filas = buscar_productos(prod, cat)
            for indice, fila in enumerate(filas):
                pid, nombre, categoria, proveedor, precio, stock = fila
                etiqueta = "par" if indice % 2 == 0 else "impar"
                self.grilla.insert(
                    "",
                    "end",
                    values=(pid, nombre, categoria, proveedor, f"${precio:.2f}", stock),
                    tags=(etiqueta,),
                )
        except psycopg2.Error as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudo consultar la vista:\n{e}")

    def _limpiar(self):
        self.ent_producto.delete(0, tk.END)
        self.ent_categoria.delete(0, tk.END)
        self._buscar()


if __name__ == "__main__":
    app = VentanaConsultaProductos()
    app.mainloop()
