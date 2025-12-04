import frappe
from frappe import _

@frappe.whitelist(allow_guest = True)
def get_translations(language='en'):
    """
    Get all translations for a specific language from Frappe's Translation doctype
    This returns a dictionary of source text -> translated text
    
    Usage: /api/method/asset_lite.api.translation_api.get_translations?language=ar
    
    Args:
        language: Language code (e.g., 'en', 'ar')
    
    Returns:
        Dictionary mapping source text to translated text
    """
    try:
        # Validate language parameter
        if not language:
            language = 'en'
        
        # Get all translations for the specified language
        translations = frappe.get_all(
            'Translation',
            filters={
                'language': language
            },
            fields=['source_text', 'translated_text'],
            limit_page_length=0  # 0 means no limit (get all)
        )
        
        # Convert to dictionary format: {source_text: translated_text}
        translation_dict = {}
        for trans in translations:
            source = trans.get('source_text')
            translated = trans.get('translated_text')
            if source and translated:
                translation_dict[source] = translated
        
        return {
            "success": True,
            "language": language,
            "count": len(translation_dict),
            "translations": translation_dict
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_translations: {str(e)}", "Translation API Error")
        return {
            "success": False,
            "error": str(e),
            "translations": {}
        }


@frappe.whitelist(allow_guest=False)
def get_available_languages():
    """
    Get list of all available languages that have translations
    
    Usage: /api/method/asset_lite.api.translation_api.get_available_languages
    
    Returns:
        List of language codes (e.g., ['en', 'ar'])
    """
    try:
        # Get distinct languages from Translation doctype
        languages = frappe.db.sql("""
            SELECT DISTINCT language 
            FROM `tabTranslation` 
            WHERE language IS NOT NULL AND language != ''
            ORDER BY language
        """, as_dict=True)
        
        language_list = [lang['language'] for lang in languages if lang.get('language')]
        
        # Always include English as default
        if 'en' not in language_list:
            language_list.insert(0, 'en')
        
        return {
            "success": True,
            "languages": language_list
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_available_languages: {str(e)}", "Translation API Error")
        return {
            "success": False,
            "error": str(e),
            "languages": ['en']
        }


@frappe.whitelist(allow_guest=False)
def get_translation(source_text, language='ar'):
    """
    Get a single translation for a specific text
    
    Usage: /api/method/asset_lite.api.translation_api.get_translation?source_text=Comprehensive&language=ar
    
    Args:
        source_text: The text to translate
        language: Target language code (default: 'ar')
    
    Returns:
        Translated text or original if not found
    """
    try:
        if not source_text:
            return {
                "success": False,
                "error": "source_text is required"
            }
        
        translation = frappe.db.get_value(
            'Translation',
            filters={
                'language': language,
                'source_text': source_text
            },
            fieldname='translated_text'
        )
        
        return {
            "success": True,
            "source_text": source_text,
            "translated_text": translation or source_text,  # Return original if not found
            "found": bool(translation)
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_translation: {str(e)}", "Translation API Error")
        return {
            "success": False,
            "error": str(e),
            "translated_text": source_text
        }