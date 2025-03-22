import uuid

# Mock product data to ensure we have something to display when scraping fails
MOCK_PRODUCTS = [
    {
        'id': str(uuid.uuid4()),
        'name': 'Neutrogena Hydro Boost Water Gel',
        'price': '₹899.00',
        'image': 'https://images-static.nykaa.com/media/catalog/product/tr:w-200,h-200,cm-pad_resize/n/e/neutrogena-hydro-boost-water-gel.jpg',
        'rating': '4.5',
        'link': '#',
        'source': 'Amazon',
        'description': 'Lightweight gel formula absorbs quickly like a gel, but has the long-lasting, intense moisturizing power of a cream. Contains hyaluronic acid, which is naturally found in the skin.',
        'category': 'moisturizer'
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'Cetaphil Moisturizing Cream',
        'price': '₹799.00',
        'image': 'https://images-static.nykaa.com/media/catalog/product/tr:w-200,h-200,cm-pad_resize/d/8/d8970e4CETAP00000052_1.jpg',
        'rating': '4.7',
        'link': '#',
        'source': 'Flipkart',
        'description': 'Rich, non-greasy cream ideal for sensitive, dry skin. Clinically proven to provide immediate and long-lasting hydration.',
        'category': 'moisturizer'
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'The Ordinary Niacinamide 10% + Zinc 1%',
        'price': '₹750.00',
        'image': 'https://images-static.nykaa.com/media/catalog/product/tr:w-200,h-200,cm-pad_resize/3/5/3548bb88904245702847_1.jpg',
        'rating': '4.3',
        'link': '#',
        'source': 'Nykaa',
        'description': 'High-strength vitamin and mineral formula to reduce the appearance of blemishes and congestion. Works to balance visible sebum activity.',
        'category': 'serum'
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'Minimalist 2% Salicylic Acid Face Wash',
        'price': '₹299.00',
        'image': 'https://images-static.nykaa.com/media/catalog/product/tr:w-200,h-200,cm-pad_resize/2/c/2ce9017MINIM00000001_1.jpg',
        'rating': '4.4',
        'link': '#',
        'source': 'Amazon',
        'description': 'Gentle cleanser with salicylic acid that removes excess oil and unclogs pores. Helps to prevent acne and blackheads.',
        'category': 'face wash'
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'Lotus Herbals Safe Sun UV Screen Matte Gel SPF 50',
        'price': '₹495.00',
        'image': 'https://images-static.nykaa.com/media/catalog/product/tr:w-200,h-200,cm-pad_resize/8/9/8904086501453_1.jpg',
        'rating': '4.1',
        'link': '#',
        'source': 'Flipkart',
        'description': 'Matte finish sunscreen with SPF 50 that protects against harmful UVA and UVB rays. Water-resistant and non-greasy formula.',
        'category': 'sunscreen'
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'Dot & Key Vitamin C Serum',
        'price': '₹695.00',
        'image': 'https://images-static.nykaa.com/media/catalog/product/tr:w-200,h-200,cm-pad_resize/d/o/dot-key-glow-reviving-vitamin-c-serum.jpg',
        'rating': '4.2',
        'link': '#',
        'source': 'Nykaa',
        'description': 'Powerful antioxidant serum with 20% Vitamin C that brightens skin, reduces dark spots and boosts collagen production.',
        'category': 'serum'
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'Bioderma Sensibio H2O Micellar Water',
        'price': '₹1,250.00',
        'image': 'https://images-static.nykaa.com/media/catalog/product/tr:w-200,h-200,cm-pad_resize/n/y/nykbioderma1.jpg',
        'rating': '4.7',
        'link': '#',
        'source': 'Amazon',
        'description': 'Gentle cleansing micellar water that removes makeup and impurities without rinsing. Perfect for sensitive skin.',
        'category': 'cleanser'
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'Clinique Moisture Surge 100H',
        'price': '₹1,950.00',
        'image': 'https://images-static.nykaa.com/media/catalog/product/tr:w-200,h-200,cm-pad_resize/8/2/8242777_1.jpg',
        'rating': '4.6',
        'link': '#',
        'source': 'Flipkart',
        'description': 'Oil-free gel-cream that delivers 100 hours of moisture. With auto-replenishing technology that helps skin create its own internal water source.',
        'category': 'moisturizer'
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'Simple Kind to Skin Refreshing Facial Wash',
        'price': '₹375.00',
        'image': 'https://images-static.nykaa.com/media/catalog/product/tr:w-200,h-200,cm-pad_resize/2/3/2324917simple_facial_wash.jpg',
        'rating': '4.3',
        'link': '#',
        'source': 'Nykaa',
        'description': 'A gentle face wash that cleanses and refreshes without drying. Perfect for sensitive skin, with no artificial perfumes or harsh chemicals.',
        'category': 'face wash'
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'Forest Essentials Soundarya Radiance Cream',
        'price': '₹3,450.00',
        'image': 'https://images-static.nykaa.com/media/catalog/product/tr:w-200,h-200,cm-pad_resize/f/o/forest-essentials-soundarya-radiance-cream-with-spf25-50g.jpg',
        'rating': '4.5',
        'link': '#',
        'source': 'Amazon',
        'description': 'Luxurious Ayurvedic moisturizer with 24K gold that nourishes and illuminates the skin. Enriched with herbs and pure cold-pressed oils.',
        'category': 'moisturizer'
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'The Face Shop Rice Water Bright Cleansing Foam',
        'price': '₹598.00',
        'image': 'https://images-static.nykaa.com/media/catalog/product/tr:w-200,h-200,cm-pad_resize/t/h/thefaceshop_ricewater_.jpg',
        'rating': '4.0',
        'link': '#',
        'source': 'Flipkart',
        'description': 'Deeply cleanses and brightens skin with rice extract. Removes impurities and makeup residue while maintaining skin\'s moisture balance.',
        'category': 'face wash'
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'L\'Oreal Paris Revitalift 1.5% Hyaluronic Acid Serum',
        'price': '₹849.00',
        'image': 'https://images-static.nykaa.com/media/catalog/product/tr:w-200,h-200,cm-pad_resize/l/o/loreal-paris-revitalift-15_-hyaluronic-acid-serum.jpg',
        'rating': '4.4',
        'link': '#',
        'source': 'Nykaa',
        'description': 'Concentrated serum with 1.5% pure Hyaluronic Acid that instantly plumps skin and reduces wrinkles. Absorbs quickly without stickiness.',
        'category': 'serum'
    }
]

def get_mock_products(query=None, max_products=12):
    """
    Return mock products, optionally filtered by query
    """
    if not query:
        return MOCK_PRODUCTS[:max_products]
    
    query = query.lower()
    filtered_products = [p for p in MOCK_PRODUCTS if query in p['name'].lower() or 
                         query in p['description'].lower() or
                         query in p['category'].lower()]
    return filtered_products[:max_products]

def get_product_by_id(product_id):
    """
    Get a specific product by ID
    """
    for product in MOCK_PRODUCTS:
        if product['id'] == product_id:
            return product
    return None

def get_mock_cheapest_price(product_name):
    """
    Get cheapest price for a specific product name
    """
    product_name = product_name.lower()
    matches = [p for p in MOCK_PRODUCTS if product_name in p['name'].lower()]
    
    if not matches:
        return None
    
    # Find the product with the lowest price
    def extract_price(product):
        price_str = product.get('price', '0')
        if isinstance(price_str, float):
            return price_str
        return float(price_str.replace('₹', '').replace(',', ''))
        
    cheapest = min(matches, key=extract_price)
    return cheapest