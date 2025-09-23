"""
Sample data for Hurtrock Music Store
Run this script to populate the database with sample products and categories
"""

from main import app
from database import db
from models import Category, Product, ShippingService, Supplier

def create_sample_data():
    with app.app_context():
        # Check if data already exists
        if Category.query.first():
            print("Sample data already exists!")
            return

        # Create categories
        categories = [
            {
                'name': 'Gitar',
                'description': 'Koleksi gitar akustik dan elektrik berkualitas tinggi dari berbagai brand terkenal',
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400'
            },
            {
                'name': 'Drum',
                'description': 'Set drum lengkap dan aksesoris perkusi untuk segala genre musik',
                'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400'
            },
            {
                'name': 'Keyboard',
                'description': 'Piano digital dan keyboard sintetizer dengan teknologi terdepan',
                'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400'
            },
            {
                'name': 'Aksesoris',
                'description': 'Berbagai aksesoris musik dan peralatan pendukung untuk musisi',
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400'
            }
        ]

        category_objects = []
        for cat_data in categories:
            category = Category(
                name=cat_data['name'],
                description=cat_data['description'],
                image_url=cat_data['image_url']
            )
            db.session.add(category)
            category_objects.append(category)

        db.session.flush()  # Get category IDs

        # Create suppliers
        suppliers = [
            {
                'name': 'PT. Music Indonesia',
                'contact_person': 'Budi Santoso',
                'email': 'budi@musicindonesia.com',
                'phone': '021-12345678',
                'address': 'Jl. Musik Raya No. 123, Jakarta Selatan',
                'company': 'PT. Music Indonesia',
                'notes': 'Supplier utama untuk produk Yamaha dan Roland'
            },
            {
                'name': 'CV. Harmoni Nada',
                'contact_person': 'Siti Rahayu',
                'email': 'siti@harmoninada.co.id',
                'phone': '021-87654321',
                'address': 'Jl. Harmoni No. 456, Jakarta Pusat',
                'company': 'CV. Harmoni Nada',
                'notes': 'Spesialis gitar Fender dan Gibson'
            },
            {
                'name': 'UD. Drum Center',
                'contact_person': 'Ahmad Fadli',
                'email': 'ahmad@drumcenter.com',
                'phone': '021-11223344',
                'address': 'Jl. Beat No. 789, Bandung',
                'company': 'UD. Drum Center',
                'notes': 'Distributor drum Pearl dan Tama'
            },
            {
                'name': 'Toko Aksesoris Musik',
                'contact_person': 'Lisa Permata',
                'email': 'lisa@aksesorismusik.com',
                'phone': '031-55667788',
                'address': 'Jl. Melody No. 321, Surabaya',
                'company': 'Toko Aksesoris Musik',
                'notes': 'Supplier aksesoris dan spare parts'
            }
        ]

        supplier_objects = []
        for supplier_data in suppliers:
            supplier = Supplier(
                name=supplier_data['name'],
                contact_person=supplier_data['contact_person'],
                email=supplier_data['email'],
                phone=supplier_data['phone'],
                address=supplier_data['address'],
                company=supplier_data['company'],
                notes=supplier_data['notes']
            )
            db.session.add(supplier)
            supplier_objects.append(supplier)

        db.session.flush()  # Get supplier IDs

        # Create products
        products = [
            # Gitar
            {
                'name': 'Yamaha F310 Acoustic Guitar',
                'description': 'Gitar akustik entry-level dengan kualitas suara yang jernih dan build quality yang solid. Cocok untuk pemula hingga intermediate.',
                'price': 1850000,
                'stock_quantity': 15,
                'brand': 'Yamaha',
                'model': 'F310',
                'category_id': category_objects[0].id,
                'supplier_id': supplier_objects[0].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500',
                'weight': 2200, 'length': 104, 'width': 38, 'height': 12
            },
            {
                'name': 'Fender Player Stratocaster',
                'description': 'Gitar elektrik legendaris dengan tone versatile dan playability yang luar biasa. Dilengkapi pickup single-coil yang iconic.',
                'price': 12500000,
                'stock_quantity': 8,
                'brand': 'Fender',
                'model': 'Player Stratocaster',
                'category_id': category_objects[0].id,
                'supplier_id': supplier_objects[1].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?w=500',
                'weight': 3500, 'length': 99, 'width': 32, 'height': 5
            },
            {
                'name': 'Gibson Les Paul Standard',
                'description': 'Gitar elektrik premium dengan sustain yang panjang dan tone yang warm. Ideal untuk rock dan blues.',
                'price': 28500000,
                'stock_quantity': 3,
                'brand': 'Gibson',
                'model': 'Les Paul Standard',
                'category_id': category_objects[0].id,
                'supplier_id': supplier_objects[1].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1556449895-a33c9dba33dd?w=500',
                'weight': 4100, 'length': 96, 'width': 34, 'height': 5
            },

            # Drum
            {
                'name': 'Pearl Export Series Drum Kit',
                'description': 'Set drum lengkap 5-piece dengan hardware dan cymbal. Suara yang powerful dan punch untuk berbagai genre.',
                'price': 8750000,
                'stock_quantity': 6,
                'brand': 'Pearl',
                'model': 'Export Series',
                'category_id': category_objects[1].id,
                'supplier_id': supplier_objects[2].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=500',
                'weight': 35000, 'length': 150, 'width': 120, 'height': 80
            },
            {
                'name': 'Tama Imperialstar Complete Kit',
                'description': 'Drum kit pemula yang lengkap dengan cymbal dan hardware berkualitas. Mudah di-setup dan tuning.',
                'price': 6250000,
                'stock_quantity': 4,
                'brand': 'Tama',
                'model': 'Imperialstar',
                'category_id': category_objects[1].id,
                'supplier_id': supplier_objects[2].id,
                'image_url': 'https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?w=500',
                'weight': 32000, 'length': 140, 'width': 110, 'height': 75
            },

            # Keyboard
            {
                'name': 'Yamaha PSR-E373 Keyboard',
                'description': 'Keyboard 61-key dengan 622 suara dan 205 style. Touch response dan learning function untuk pemula.',
                'price': 2750000,
                'stock_quantity': 12,
                'brand': 'Yamaha',
                'model': 'PSR-E373',
                'category_id': category_objects[2].id,
                'supplier_id': supplier_objects[0].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500',
                'weight': 4500, 'length': 94, 'width': 31, 'height': 10
            },
            {
                'name': 'Casio CDP-S110 Digital Piano',
                'description': 'Piano digital 88-key dengan weighted action dan 10 built-in tones. Desain compact dan portable.',
                'price': 4950000,
                'stock_quantity': 7,
                'brand': 'Casio',
                'model': 'CDP-S110',
                'category_id': category_objects[2].id,
                'supplier_id': supplier_objects[3].id,
                'image_url': 'https://images.unsplash.com/photo-1520523839897-bd0b52f915a0?w=500',
                'weight': 10500, 'length': 132, 'width': 29, 'height': 10
            },
            {
                'name': 'Roland FP-30X Digital Piano',
                'description': 'Piano digital premium dengan SuperNATURAL Piano sound dan PHA-4 Standard keyboard untuk feel yang authentic.',
                'price': 9850000,
                'stock_quantity': 5,
                'brand': 'Roland',
                'model': 'FP-30X',
                'category_id': category_objects[2].id,
                'supplier_id': supplier_objects[0].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1549298327-ffb31f3a7249?w=500',
                'weight': 16500, 'length': 130, 'width': 28, 'height': 15
            },

            # Aksesoris
            {
                'name': 'Audio-Technica ATH-M50x Headphones',
                'description': 'Headphone monitoring profesional dengan sound signature yang balanced dan build quality yang robust.',
                'price': 1850000,
                'stock_quantity': 20,
                'brand': 'Audio-Technica',
                'model': 'ATH-M50x',
                'category_id': category_objects[3].id,
                'supplier_id': supplier_objects[3].id,
                'image_url': 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500',
                'weight': 285, 'length': 20, 'width': 18, 'height': 8
            },
            {
                'name': 'Shure SM58 Dynamic Microphone',
                'description': 'Mikrofon dinamis legendaris untuk vokal live dan recording. Durability dan clarity yang terjamin.',
                'price': 1650000,
                'stock_quantity': 15,
                'brand': 'Shure',
                'model': 'SM58',
                'category_id': category_objects[3].id,
                'supplier_id': supplier_objects[3].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1590736969955-71cc94901144?w=500',
                'weight': 298, 'length': 16, 'width': 5, 'height': 5
            },
            {
                'name': 'Boss DS-1 Distortion Pedal',
                'description': 'Pedal distortion klasik dengan tone yang aggressive dan sustain yang smooth. Essential untuk rock dan metal.',
                'price': 1250000,
                'stock_quantity': 25,
                'brand': 'Boss',
                'model': 'DS-1',
                'category_id': category_objects[3].id,
                'supplier_id': supplier_objects[3].id,
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500',
                'weight': 400, 'length': 12, 'width': 7, 'height': 6
            },
            {
                'name': 'Ernie Ball Regular Slinky Guitar Strings',
                'description': 'Senar gitar elektrik gauge 10-46 dengan tone yang bright dan sustain yang excellent. Durability tinggi.',
                'price': 185000,
                'stock_quantity': 50,
                'brand': 'Ernie Ball',
                'model': 'Regular Slinky',
                'category_id': category_objects[3].id,
                'supplier_id': supplier_objects[3].id,
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500',
                'weight': 50, 'length': 15, 'width': 10, 'height': 1
            }
        ]

        for product_data in products:
            product = Product(
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                stock_quantity=product_data['stock_quantity'],
                brand=product_data['brand'],
                model=product_data['model'],
                category_id=product_data['category_id'],
                supplier_id=product_data['supplier_id'],
                is_featured=product_data.get('is_featured', False),
                image_url=product_data['image_url'],
                weight=product_data.get('weight'),
                length=product_data.get('length'),
                width=product_data.get('width'),
                height=product_data.get('height')
            )
            db.session.add(product)

        # Create sample shipping services
        shipping_services = [
            {
                'name': 'JNE Regular',
                'code': 'jne_reg',
                'base_price': 15000,
                'price_per_kg': 8000,
                'price_per_km': 0.5,
                'volume_factor': 6000,
                'min_days': 2,
                'max_days': 4
            },
            {
                'name': 'JNE Express',
                'code': 'jne_exp',
                'base_price': 25000,
                'price_per_kg': 12000,
                'price_per_km': 0.8,
                'volume_factor': 5000,
                'min_days': 1,
                'max_days': 2
            },
            {
                'name': 'JNT Express',
                'code': 'jnt_exp',
                'base_price': 12000,
                'price_per_kg': 7000,
                'price_per_km': 0.4,
                'volume_factor': 6000,
                'min_days': 2,
                'max_days': 5
            },
            {
                'name': 'SiCepat Regular',
                'code': 'sicepat_reg',
                'base_price': 14000,
                'price_per_kg': 7500,
                'price_per_km': 0.45,
                'volume_factor': 5500,
                'min_days': 2,
                'max_days': 4
            },
            {
                'name': 'Pos Indonesia',
                'code': 'pos_reg',
                'base_price': 10000,
                'price_per_kg': 6000,
                'price_per_km': 0.3,
                'volume_factor': 7000,
                'min_days': 3,
                'max_days': 7
            }
        ]

        for service_data in shipping_services:
            service = ShippingService(
                name=service_data['name'],
                code=service_data['code'],
                base_price=service_data['base_price'],
                price_per_kg=service_data['price_per_kg'],
                price_per_km=service_data['price_per_km'],
                volume_factor=service_data['volume_factor'],
                min_days=service_data['min_days'],
                max_days=service_data['max_days']
            )
            db.session.add(service)

        db.session.commit()
        print("Sample data created successfully!")
        print(f"Created {len(categories)} categories, {len(products)} products, {len(shipping_services)} shipping services, and {len(suppliers)} suppliers")

def create_suppliers_and_products():
    """Create suppliers and products from Swelee, Media Recording Tech, and Triple 3 Music Store"""
    with app.app_context():
        from models import Supplier, Product, Category
        
        # Check if suppliers already exist
        if Supplier.query.filter_by(name='Swelee').first():
            print("Suppliers Swelee, Media Recording Tech, dan Triple 3 Music Store sudah ada!")
            return
        
        # Create the three requested suppliers
        suppliers_data = [
            {
                'name': 'Swelee',
                'contact_person': 'John Swelee',
                'email': 'contact@swelee.com',
                'phone': '021-555-0101',
                'address': 'Jl. Musik Digital No. 45, Jakarta Barat',
                'company': 'PT. Swelee Indonesia',
                'notes': 'Supplier peralatan musik digital dan aksesoris premium'
            },
            {
                'name': 'Media Recording Tech',
                'contact_person': 'Sarah Mitchell',
                'email': 'sales@mediarecordingtech.com',
                'phone': '021-555-0202',
                'address': 'Jl. Studio Raya No. 78, Jakarta Selatan',
                'company': 'CV. Media Recording Technology',
                'notes': 'Spesialis peralatan recording dan produksi musik profesional'
            },
            {
                'name': 'Triple 3 Music Store',
                'contact_person': 'Ahmad Rahman',
                'email': 'info@triple3music.co.id',
                'phone': '021-555-0303',
                'address': 'Jl. Harmoni Musik No. 333, Jakarta Pusat',
                'company': 'PT. Triple 3 Music Indonesia',
                'notes': 'Distributor resmi berbagai brand alat musik internasional'
            }
        ]
        
        supplier_objects = []
        for supplier_data in suppliers_data:
            supplier = Supplier(**supplier_data)
            db.session.add(supplier)
            supplier_objects.append(supplier)
        
        db.session.flush()  # Get supplier IDs
        
        # Get categories
        gitar_cat = Category.query.filter_by(name='Gitar').first()
        drum_cat = Category.query.filter_by(name='Drum').first()
        keyboard_cat = Category.query.filter_by(name='Keyboard').first()
        aksesoris_cat = Category.query.filter_by(name='Aksesoris').first()
        
        # Create 10 products from these suppliers
        products_data = [
            # Products from Swelee (3 products)
            {
                'name': 'Swelee Digital Piano SWL-DP88',
                'description': 'Piano digital 88 tuts dengan weighted keys dan 500+ sounds berkualitas studio. Dilengkapi koneksi MIDI dan USB.',
                'price': 8500000,
                'stock_quantity': 12,
                'brand': 'Swelee',
                'model': 'SWL-DP88',
                'category_id': keyboard_cat.id,
                'supplier_id': supplier_objects[0].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500',
                'weight': 45000, 'length': 135, 'width': 35, 'height': 15
            },
            {
                'name': 'Swelee Audio Interface SWL-AI24',
                'description': 'Audio interface 24-bit dengan 2 input XLR/TRS dan monitoring real-time. Cocok untuk home recording.',
                'price': 2750000,
                'stock_quantity': 20,
                'brand': 'Swelee',
                'model': 'SWL-AI24',
                'category_id': aksesoris_cat.id,
                'supplier_id': supplier_objects[0].id,
                'image_url': 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=500',
                'weight': 800, 'length': 25, 'width': 18, 'height': 5
            },
            {
                'name': 'Swelee Synthesizer SWL-SYNTH Pro',
                'description': 'Analog synthesizer dengan 61 tuts dan built-in arpeggiator. Ideal untuk produksi musik elektronik.',
                'price': 12500000,
                'stock_quantity': 8,
                'brand': 'Swelee',
                'model': 'SWL-SYNTH Pro',
                'category_id': keyboard_cat.id,
                'supplier_id': supplier_objects[0].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500',
                'weight': 12000, 'length': 95, 'width': 32, 'height': 12
            },
            
            # Products from Media Recording Tech (4 products)
            {
                'name': 'MRT Studio Monitor Pro-8',
                'description': 'Studio monitor aktif 8 inch dengan response frequency yang flat. Ideal untuk mixing dan mastering profesional.',
                'price': 6500000,
                'stock_quantity': 10,
                'brand': 'Media Recording Tech',
                'model': 'Pro-8',
                'category_id': aksesoris_cat.id,
                'supplier_id': supplier_objects[1].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500',
                'weight': 8500, 'length': 35, 'width': 25, 'height': 30
            },
            {
                'name': 'MRT Condenser Microphone CM-100',
                'description': 'Microphone condenser large diaphragm dengan polar pattern cardioid. Suara jernih untuk vocal recording.',
                'price': 3250000,
                'stock_quantity': 15,
                'brand': 'Media Recording Tech',
                'model': 'CM-100',
                'category_id': aksesoris_cat.id,
                'supplier_id': supplier_objects[1].id,
                'image_url': 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=500',
                'weight': 600, 'length': 20, 'width': 8, 'height': 8
            },
            {
                'name': 'MRT Mixing Console MX-16',
                'description': 'Mixing console 16 channel dengan EQ 3-band dan efek built-in. Cocok untuk studio kecil hingga menengah.',
                'price': 15750000,
                'stock_quantity': 5,
                'brand': 'Media Recording Tech',
                'model': 'MX-16',
                'category_id': aksesoris_cat.id,
                'supplier_id': supplier_objects[1].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500',
                'weight': 25000, 'length': 60, 'width': 45, 'height': 15
            },
            {
                'name': 'MRT Recording Headphones RH-Pro',
                'description': 'Headphones studio dengan driver 50mm dan impedansi 32 ohm. Comfortable untuk monitoring selama berjam-jam.',
                'price': 1850000,
                'stock_quantity': 25,
                'brand': 'Media Recording Tech',
                'model': 'RH-Pro',
                'category_id': aksesoris_cat.id,
                'supplier_id': supplier_objects[1].id,
                'image_url': 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=500',
                'weight': 350, 'length': 25, 'width': 20, 'height': 10
            },
            
            # Products from Triple 3 Music Store (3 products)
            {
                'name': 'Triple3 Electric Guitar T3-EG500',
                'description': 'Gitar elektrik solid body dengan pickup humbucker dan tremolo bridge. Tone versatile untuk segala genre.',
                'price': 4250000,
                'stock_quantity': 18,
                'brand': 'Triple 3',
                'model': 'T3-EG500',
                'category_id': gitar_cat.id,
                'supplier_id': supplier_objects[2].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?w=500',
                'weight': 3200, 'length': 98, 'width': 33, 'height': 5
            },
            {
                'name': 'Triple3 Drum Kit T3-DK800',
                'description': 'Drum kit lengkap 7-piece dengan hardware dan cymbal set. Suara balanced untuk rock dan pop.',
                'price': 12500000,
                'stock_quantity': 6,
                'brand': 'Triple 3',
                'model': 'T3-DK800',
                'category_id': drum_cat.id,
                'supplier_id': supplier_objects[2].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=500',
                'weight': 85000, 'length': 200, 'width': 150, 'height': 120
            },
            {
                'name': 'Triple3 Bass Guitar T3-BG400',
                'description': 'Bass elektrik 4-string dengan pickup active dan preamp built-in. Low-end yang tight dan punchy.',
                'price': 5750000,
                'stock_quantity': 12,
                'brand': 'Triple 3',
                'model': 'T3-BG400',
                'category_id': gitar_cat.id,
                'supplier_id': supplier_objects[2].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500',
                'weight': 4500, 'length': 115, 'width': 35, 'height': 6
            }
        ]
        
        # Add products to database
        for product_data in products_data:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        print("[OK] Supplier Swelee, Media Recording Tech, dan Triple 3 Music Store beserta 10 produknya berhasil ditambahkan!")

if __name__ == '__main__':
    create_sample_data()