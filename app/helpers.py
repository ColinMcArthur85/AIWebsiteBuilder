import re
from jinja2 import Template

# Helper function to find background color in the content
def extract_background_color(content):
    match = re.search(r'background-color:\s*(#[A-Fa-f0-9]{6}|#[A-Fa-f0-9]{3}|rgba?\([^)]+\)|[a-zA-Z]+);', content)
    if match:
        return match.group(1)
    return None

# Helper function to enforce background rules without boilerplate
def enforce_immutable_rules(generated_code, section_background_color):
    if section_background_color is None:
        section_background_color = "#ffffff"  # Default background color

    return f'''
    <section style="background:{section_background_color};background-size:cover;background-repeat:no-repeat;">
        <div class="content-wrap nopadding">
            <div class="section notopborder nomargin toppadding-sm bottompadding-sm" style="background:transparent;">
                <div class="container clearfix">
                    {generated_code}
                </div>
            </div>
        </div>
    </section>
    '''

def generate_button_html(content, button_background_color, border_color, text_color):
    return f'''
    <a href="#" class="btn-block edit-button-style button button-3d button-rounded button-default"
       style="background-color: {button_background_color}; border-color: {border_color}; color: {text_color};"
       data-button-class-name="">{content}</a>
    '''