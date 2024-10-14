from types import SimpleNamespace

def default_home_page_section(products): 

    data = {
        "id": "top-picks",
        'section_id' : "top-picks",
        "title": "Top picks",
        "products": products,
        "type": "products-container",
        "active": True,
        "image": None,
        "design": {
            "mobile": {
                "marginTop": 4,
                "marginHorizontal": 4,
                "backgroundColor": {
                    "light": "#00000000",
                    "dark": "#121212"
                },
                "title": {
                    "showTitle": False,
                    "size": 26,
                    "direction": "center",
                    "bordersRounded": None,
                    "padding": 0,
                    "label": {
                        "color": {
                            "light": "#72543c",
                            "dark": "#bca08a"
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
                        "dark": "#121212"
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
                    "showTitle": False,
                    "size": 23,
                    "direction": "start",
                    "padding": 8,
                    "label": {
                        "color": {
                            "light": "#bca08a",
                            "dark": "#bca08a"
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
                        "dark": "#121212"
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
                                "light": "#754f32",
                                "dark": "#bca08a"
                            }
                        }
                    },
                    "bordersRounded": False
                }
            }
        },
        "device": [
            "mobile",
            "PC"
        ]
    }
    return SimpleNamespace(**data) 