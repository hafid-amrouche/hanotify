from types import SimpleNamespace

primary = {
    'light': '#446ec3',
    'dark': '#446ec3'
}

def default_design(primary=primary): {
    "mobile": {
        "marginTop": 4,
        "marginHorizontal": 4,
        "backgroundColor": {
            "light": "#00000000",
            "dark": "#00000000"
        },
        "title": {
            "showTitle": True,
            "size": 26,
            "direction": "center",
            "bordersRounded": None,
            "padding": 0,
            "label": {
                "color": {
                    "light": primary['light'],
                    "dark": primary['dark'],
                }
            }
        },
        "products": {
            "productsDisplay": "simple",
            "justifyContent": "center",
            "gap": 8,
            "bordersRounded": True,
            "borderWidth": 1,
            "backgroundColor": {
                "light": "#00000000",
                "dark": "#00000000"
            },
            "borderColor": {
                "light": "#80808060",
                "dark": "#50505080"
            },
            "product": {
                "width": "50%",
                "image": {
                    "objectFit": "cover",
                    "aspectRatio": "1/1"
                },
                "title": {
                    "size": 18,
                    "color": {
                        "light": "#11181C",
                        "dark": "#ffffff"
                    }
                },
                "price": {
                    "size": 18,
                    "color": {
                        "light": "#754f32",
                        "dark": "#bca08a"
                    }
                }
            }
        }
    },
    "PC": {
        "marginTop": 10,
        "marginHorizontal": 8,
        "backgroundColor": {
            "light": "#00000000",
            "dark": "#121212"
        },
        "title": {
            "showTitle": True,
            "size": 23,
            "direction": "start",
            "padding": 8,
            "label": {
                "color": {
                    "light": primary['light'],
                    "dark": primary['dark']
                }
            }
        },
        "products": {
            "productsDisplay": "simple",
            "justifyContent": "center",
            "gap": 8,
            "borderWidth": 1,
            "backgroundColor": {
                "light": "#00000000",
                "dark": "#00000000"
            },
            "borderColor": {
                "light": "#80808060",
                "dark": "#50505080"
            },
            "product": {
                "width": "220px",
                "image": {
                    "aspectRatio": "1/1",
                    "objectFit": "cover"
                },
                "title": {
                    "size": 22,
                    "color": {
                        "light": "#11181C",
                        "dark": "#ffffff"
                    }
                },
                "price": {
                    "size": 16,
                    "color": {
                        "light": primary['light'],
                        "dark": primary['dark']
                    }
                }
            },
            "bordersRounded": False
        }
    }
}
        

def default_home_page_section(products, design, title): 
    data={
        "id": "default-section",
        'section_id' : "default-section",
        "title": title,
        "products": products,
        "type": "products-container",
        "active": True,
        "image": None,
        "show_latest_products": None,
        "lastest_products_count": 12,
        "design": design,
        "device": [
            "mobile",
            "PC"
        ]
    }
    return SimpleNamespace(**data) 