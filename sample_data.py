"""
Sample data for Hurtrock Music Store
Run this script to populate the database with sample products and categories
"""

from main import app
from database import db
from models import Category, Product

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
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500'
            },
            {
                'name': 'Fender Player Stratocaster',
                'description': 'Gitar elektrik legendaris dengan tone versatile dan playability yang luar biasa. Dilengkapi pickup single-coil yang iconic.',
                'price': 12500000,
                'stock_quantity': 8,
                'brand': 'Fender',
                'model': 'Player Stratocaster',
                'category_id': category_objects[0].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?w=500'
            },
            {
                'name': 'Gibson Les Paul Standard',
                'description': 'Gitar elektrik premium dengan sustain yang panjang dan tone yang warm. Ideal untuk rock dan blues.',
                'price': 28500000,
                'stock_quantity': 3,
                'brand': 'Gibson',
                'model': 'Les Paul Standard',
                'category_id': category_objects[0].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1556449895-a33c9dba33dd?w=500'
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
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=500'
            },
            {
                'name': 'Tama Imperialstar Complete Kit',
                'description': 'Drum kit pemula yang lengkap dengan cymbal dan hardware berkualitas. Mudah di-setup dan tuning.',
                'price': 6250000,
                'stock_quantity': 4,
                'brand': 'Tama',
                'model': 'Imperialstar',
                'category_id': category_objects[1].id,
                'image_url': 'https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?w=500'
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
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500'
            },
            {
                'name': 'Casio CDP-S110 Digital Piano',
                'description': 'Piano digital 88-key dengan weighted action dan 10 built-in tones. Desain compact dan portable.',
                'price': 4950000,
                'stock_quantity': 7,
                'brand': 'Casio',
                'model': 'CDP-S110',
                'category_id': category_objects[2].id,
                'image_url': 'https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?w=500'
            },
            {
                'name': 'Roland FP-30X Digital Piano',
                'description': 'Piano digital premium dengan SuperNATURAL Piano sound dan PHA-4 Standard keyboard untuk feel yang authentic.',
                'price': 9850000,
                'stock_quantity': 5,
                'brand': 'Roland',
                'model': 'FP-30X',
                'category_id': category_objects[2].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1549298327-ffb31f3a7249?w=500'
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
                'image_url': 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500'
            },
            {
                'name': 'Shure SM58 Dynamic Microphone',
                'description': 'Mikrofon dinamis legendaris untuk vokal live dan recording. Durability dan clarity yang terjamin.',
                'price': 1650000,
                'stock_quantity': 15,
                'brand': 'Shure',
                'model': 'SM58',
                'category_id': category_objects[3].id,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1590736969955-71cc94901144?w=500'
            },
            {
                'name': 'Boss DS-1 Distortion Pedal',
                'description': 'Pedal distortion klasik dengan tone yang aggressive dan sustain yang smooth. Essential untuk rock dan metal.',
                'price': 1250000,
                'stock_quantity': 25,
                'brand': 'Boss',
                'model': 'DS-1',
                'category_id': category_objects[3].id,
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500'
            },
            {
                'name': 'Ernie Ball Regular Slinky Guitar Strings',
                'description': 'Senar gitar elektrik gauge 10-46 dengan tone yang bright dan sustain yang excellent. Durability tinggi.',
                'price': 185000,
                'stock_quantity': 50,
                'brand': 'Ernie Ball',
                'model': 'Regular Slinky',
                'category_id': category_objects[3].id,
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500'
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
                is_featured=product_data.get('is_featured', False),
                image_url=product_data['image_url']
            )
            db.session.add(product)
        
        db.session.commit()
        print("Sample data created successfully!")
        print(f"Created {len(categories)} categories and {len(products)} products")

if __name__ == '__main__':
    create_sample_data()