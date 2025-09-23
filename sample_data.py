
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
            },
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
            },

            # 10 New Products from Swelee, Media Recording Tech, and Triple 3
            {
                'name': 'Swelee Digital Piano Pro-88',
                'description': 'Piano digital premium 88 tuts weighted dengan 1000+ sounds dan fitur recording built-in. Koneksi Bluetooth dan USB untuk modern musician.',
                'price': 15750000,
                'stock_quantity': 8,
                'brand': 'Swelee',
                'model': 'Pro-88',
                'category_id': category_objects[2].id,
                'supplier_id': supplier_objects[4].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1571974599782-87624638275c?w=500',
                'weight': 52000, 'length': 138, 'width': 36, 'height': 16
            },
            {
                'name': 'Swelee Studio Monitor SM-8',
                'description': 'Monitor studio aktif 8 inch dengan response frequency yang flat dan akurat. Perfect untuk mixing dan mastering di home studio.',
                'price': 5850000,
                'stock_quantity': 12,
                'brand': 'Swelee',
                'model': 'SM-8',
                'category_id': category_objects[3].id,
                'supplier_id': supplier_objects[4].id,
                'image_url': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500',
                'weight': 9500, 'length': 32, 'width': 23, 'height': 28
            },
            {
                'name': 'Media Recording Condenser Mic MC-Pro',
                'description': 'Mikrofon kondenser large diaphragm dengan pattern cardioid dan shock mount. Ideal untuk vocal recording dan podcasting.',
                'price': 3750000,
                'stock_quantity': 15,
                'brand': 'Media Recording Tech',
                'model': 'MC-Pro',
                'category_id': category_objects[3].id,
                'supplier_id': supplier_objects[5].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=500',
                'weight': 650, 'length': 22, 'width': 8, 'height': 8
            },
            {
                'name': 'Media Recording Audio Interface AI-24',
                'description': 'Audio interface 24-bit/192kHz dengan 4 input dan 4 output. Zero-latency monitoring dan MIDI I/O untuk profesional recording.',
                'price': 4250000,
                'stock_quantity': 10,
                'brand': 'Media Recording Tech',
                'model': 'AI-24',
                'category_id': category_objects[3].id,
                'supplier_id': supplier_objects[5].id,
                'image_url': 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=500',
                'weight': 1200, 'length': 28, 'width': 20, 'height': 6
            },
            {
                'name': 'Media Recording Mixing Console MX-24',
                'description': 'Mixing console analog 24 channel dengan EQ 4-band dan built-in effects. Professional sound untuk live performance dan recording.',
                'price': 28500000,
                'stock_quantity': 3,
                'brand': 'Media Recording Tech',
                'model': 'MX-24',
                'category_id': category_objects[3].id,
                'supplier_id': supplier_objects[5].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500',
                'weight': 35000, 'length': 75, 'width': 55, 'height': 18
            },
            {
                'name': 'Triple 3 Electric Guitar T3-LES Pro',
                'description': 'Gitar elektrik solid body dengan pickup humbucker dan mahogany body. Tone yang warm dan sustain panjang untuk rock dan blues.',
                'price': 8750000,
                'stock_quantity': 6,
                'brand': 'Triple 3',
                'model': 'T3-LES Pro',
                'category_id': category_objects[0].id,
                'supplier_id': supplier_objects[6].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1525201548942-d8732f6617a0?w=500',
                'weight': 3800, 'length': 97, 'width': 34, 'height': 5
            },
            {
                'name': 'Triple 3 Bass Guitar T3-JAZZ Bass',
                'description': 'Bass elektrik 4-string dengan pickup jazz bass dan active preamp. Tone yang punchy dan artikulasi yang jelas untuk semua genre.',
                'price': 6850000,
                'stock_quantity': 8,
                'brand': 'Triple 3',
                'model': 'T3-JAZZ',
                'category_id': category_objects[0].id,
                'supplier_id': supplier_objects[6].id,
                'image_url': 'https://images.unsplash.com/photo-1520637836862-4d197d17c2a2?w=500',
                'weight': 4200, 'length': 116, 'width': 36, 'height': 6
            },
            {
                'name': 'Triple 3 Drum Kit T3-ROCK Series',
                'description': 'Drum kit rock series 6-piece dengan shell birch dan hardware chrome. Suara yang powerful dan attack yang tajam.',
                'price': 18500000,
                'stock_quantity': 4,
                'brand': 'Triple 3',
                'model': 'T3-ROCK',
                'category_id': category_objects[1].id,
                'supplier_id': supplier_objects[6].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1519508234761-0de1373c8df6?w=500',
                'weight': 65000, 'length': 180, 'width': 140, 'height': 100
            },
            {
                'name': 'Triple 3 Acoustic Guitar T3-FOLK',
                'description': 'Gitar akustik folk dengan top solid spruce dan back mahogany. Tone yang balanced dan projection yang excellent untuk fingerpicking.',
                'price': 4750000,
                'stock_quantity': 10,
                'brand': 'Triple 3',
                'model': 'T3-FOLK',
                'category_id': category_objects[0].id,
                'supplier_id': supplier_objects[6].id,
                'image_url': 'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=500',
                'weight': 2400, 'length': 105, 'width': 39, 'height': 13
            },
            {
                'name': 'Swelee Synthesizer SWL-ANALOG Pro',
                'description': 'Analog synthesizer dengan 49 tuts dan built-in sequencer. Authentic analog sound dengan modern connectivity untuk electronic music production.',
                'price': 22500000,
                'stock_quantity': 5,
                'brand': 'Swelee',
                'model': 'SWL-ANALOG Pro',
                'category_id': category_objects[2].id,
                'supplier_id': supplier_objects[4].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500',
                'weight': 15000, 'length': 85, 'width': 35, 'height': 14
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

if __name__ == '__main__':
    create_sample_data()
