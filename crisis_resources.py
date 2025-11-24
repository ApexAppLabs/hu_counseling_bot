"""
Crisis Resources Configuration
Customize these resources for your region/country
"""

# Default crisis resources (edit these for your region)
CRISIS_RESOURCES = {
    'default': {
        'hotlines': [
            {
                'name': 'Local crisis support',
                'number': 'Contact your university clinic, counseling office, or local health centre',
                'region': 'Local',
            },
            {
                'name': 'Trusted people around you',
                'number': 'Reach out to a close friend, family member, fellowship leader, or university staff',
                'region': 'Local',
            },
        ],
        'emergency': 'Local emergency services / campus security',
        'additional_text': 'If you are in immediate danger or feel you might harm yourself or someone else, please seek help around you immediately (nearby people, university clinic, health centre, hospital, or campus security).'
    },
    
    # Add your region-specific resources here
    # Example for UK:
    # 'UK': {
    #     'hotlines': [
    #         {'name': 'Samaritans', 'number': '116 123', 'region': 'UK'},
    #         {'name': 'Crisis Text Line UK', 'number': 'Text SHOUT to 85258', 'region': 'UK'},
    #     ],
    #     'emergency': '999',
    #     'additional_text': 'If you are in immediate danger, please call 999 or go to A&E.'
    # },
    
    # Example for International:
    # 'international': {
    #     'hotlines': [
    #         {'name': 'Befrienders Worldwide', 'number': 'Visit befrienders.org', 'region': 'Global'},
    #         {'name': 'International Association for Suicide Prevention', 'number': 'Visit iasp.info/resources', 'region': 'Global'},
    #     ],
    #     'emergency': 'Local emergency services',
    #     'additional_text': 'If you are in immediate danger, please contact your local emergency services.'
    # }
}

def get_crisis_text(region='default'):
    """
    Get crisis resources text for a specific region
    
    Args:
        region: Region code (default, UK, international, etc.)
        
    Returns:
        Formatted text string with crisis resources
    """
    resources = CRISIS_RESOURCES.get(region, CRISIS_RESOURCES['default'])
    
    text = f"⚠️ **{resources['additional_text']}**\n\n"
    text += f"**Emergency:** {resources['emergency']}\n\n"
    text += "**Crisis Resources:**\n"
    
    for hotline in resources['hotlines']:
        text += f"• **{hotline['name']}:** {hotline['number']}\n"
    
    return text

def get_crisis_inline_text(region='default'):
    """
    Get a shorter crisis resources text for inline display
    
    Args:
        region: Region code
        
    Returns:
        Formatted text string (shorter version)
    """
    resources = CRISIS_RESOURCES.get(region, CRISIS_RESOURCES['default'])
    
    lines = []
    for hotline in resources['hotlines'][:2]:  # Show only first 2
        lines.append(f"• {hotline['name']}: {hotline['number']}")
    
    return '\n'.join(lines)

# Configuration: Set your default region here
DEFAULT_CRISIS_REGION = 'default'

# Instructions for customization
"""
TO CUSTOMIZE FOR YOUR REGION:

1. Add your region to CRISIS_RESOURCES dictionary above
2. Include local hotlines and emergency numbers
3. Update DEFAULT_CRISIS_REGION to your region code
4. Update the bot code to use these functions instead of hardcoded numbers

Example:
    from crisis_resources import get_crisis_text, DEFAULT_CRISIS_REGION
    
    crisis_info = get_crisis_text(DEFAULT_CRISIS_REGION)
    await update.message.reply_text(crisis_info)
"""
