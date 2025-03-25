import sqlite3
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.popup import Popup

DB_FILE = "products.db"

class ProductTable(GridLayout):
    def __init__(self, app, **kwargs):
        super().__init__(cols=6, size_hint_y=None, row_default_height=50, row_force_default=True)
        self.bind(minimum_height=self.setter('height'))
        self.selected_product_id = None
        self.app = app
        self.load_products()

    def load_products(self):
        self.clear_widgets()
        self.add_widget(Label(text="Nom", size_hint_x=None, width=200))
        self.add_widget(Label(text="Image", size_hint_x=None, width=200))
        self.add_widget(Label(text="Poids (kg)", size_hint_x=None, width=150))
        self.add_widget(Label(text="Prix (€)", size_hint_x=None, width=150))
        self.add_widget(Label(text="Code-barre", size_hint_x=None, width=250))
        self.add_widget(Label(text="Sélection", size_hint_x=None, width=150))
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom_produit, nom_image, poids, prix_produit, code_barre FROM products")
        products = cursor.fetchall()
        conn.close()
        
        for product in products:
            prod_id, nom, image, poids, prix, code = product
            self.add_widget(Label(text=nom, size_hint_x=None, width=200))
            self.add_widget(Label(text=image, size_hint_x=None, width=200))
            self.add_widget(Label(text=str(poids), size_hint_x=None, width=150))
            self.add_widget(Label(text=str(prix), size_hint_x=None, width=150))
            self.add_widget(Label(text=code, size_hint_x=None, width=250))
            btn_select = Button(text="Sélectionner", size_hint_x=None, width=150)
            btn_select.bind(on_press=lambda instance, pid=prod_id, pnom=nom, pimage=image, ppoids=poids, pprix=prix, pcode=code: self.select_product(pid, pnom, pimage, ppoids, pprix, pcode))
            self.add_widget(btn_select)

    def select_product(self, product_id, nom, image, poids, prix, code):
        self.selected_product_id = product_id
        self.app.populate_inputs(nom, image, poids, prix, code)

    def delete_selected_product(self):
        if self.selected_product_id:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id=?", (self.selected_product_id,))
            conn.commit()
            conn.close()
            self.selected_product_id = None
            self.load_products()

class ProductApp(App):
    def build(self):
        Window.size = (1200, 800)
        self.layout = BoxLayout(orientation='vertical')
        self.scroll_view = ScrollView(size_hint=(1, 0.8), do_scroll_x=True, do_scroll_y=True, bar_width=10)
        self.product_table = ProductTable(self, size_hint_x=None, width=1050)
        self.scroll_view.add_widget(self.product_table)
        
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2)
        self.input_nom = TextInput(hint_text='Nom', size_hint_x=0.2, font_size=24)
        self.input_image = TextInput(hint_text="Image", size_hint_x=0.2, font_size=24)
        self.input_poids = TextInput(hint_text='Poids', input_filter='float', size_hint_x=0.15, font_size=24)
        self.input_prix = TextInput(hint_text='Prix', input_filter='float', size_hint_x=0.15, font_size=24)
        self.input_code = TextInput(hint_text='Code-barre', size_hint_x=0.3, font_size=24)
        
        btn_add = Button(text='Ajouter', size_hint_x=0.2, on_press=self.add_product)
        btn_delete = Button(text='Supprimer', size_hint_x=0.2, on_press=lambda instance: self.product_table.delete_selected_product())
        
        input_layout.add_widget(self.input_nom)
        input_layout.add_widget(self.input_image)
        input_layout.add_widget(self.input_poids)
        input_layout.add_widget(self.input_prix)
        input_layout.add_widget(self.input_code)
        input_layout.add_widget(btn_add)
        input_layout.add_widget(btn_delete)
        
        self.layout.add_widget(self.scroll_view)
        self.layout.add_widget(input_layout)
        
        return self.layout
    
    def add_product(self, instance):
        nom = self.input_nom.text
        image = self.input_image.text
        poids = float(self.input_poids.text) if self.input_poids.text else 0
        prix = float(self.input_prix.text) if self.input_prix.text else 0
        code = self.input_code.text
        
        if nom and code:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products WHERE code_barre=?", (code,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO products (nom_produit, nom_image, poids, prix_produit, code_barre) VALUES (?, ?, ?, ?, ?)", (nom, image, poids, prix, code))
                conn.commit()
            else:
                self.show_error_popup("Le code-barre existe déjà!")
            conn.close()
            self.product_table.load_products()
            self.clear_inputs()
    
    def show_error_popup(self, message):
        popup = Popup(title='Erreur', content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()
    
    def clear_inputs(self):
        self.input_nom.text = ""
        self.input_image.text = ""
        self.input_poids.text = ""
        self.input_prix.text = ""
        self.input_code.text = ""
    
    def populate_inputs(self, nom, image, poids, prix, code):
        self.input_nom.text = nom
        self.input_image.text = image
        self.input_poids.text = str(poids)
        self.input_prix.text = str(prix)
        self.input_code.text = code

if __name__ == '__main__':
    ProductApp().run()
