'''
Styles dictionary for app Components
'''

styles = {
    # controls
    'controls_style': {
        'display': 'block',
        'width': '32%',
        'float': 'left',
        'height': '65vh',
        'background': '#f9f9f9',
        'boxShadow': '6px 6px 6px lightgray',
        #'overflowY': 'auto' does not allow to date picker to overflow
    },

    'search_criteria': {
        'fontSize': '16px',
        'padding': '1px 1px 1px',
        'textAlign': 'center',
        'color': '1px black',
        'display': 'flex',
        'flexWrap': 'wrap',
    },

    'filter_transactions': {
        'fontSize': '12px',
        'display': 'flex',
        'flexWrap': 'wrap',
        'paddingTop': '11px',
        'paddingLeft': '20px'
    },

    'details': {
        'padding': '10px',
        'paddingTop': '25px',
        'flexWrap': 'wrap',
        'background': '#f9f9f9',
        'boxShadow': '6px 6px 6px lightgray'
    },

    'details_label': {
        'fontSize': '19px',
        'textAlign': 'center',
        'fontWeight': 'bold',
        'flexWrap': 'wrap'
    },

    'paragraph': {
        'fontSize': '16px',
        'textAllign': 'center'
    },


    'input_form': {
        'padding': '5px',
        'margin': 'auto',
        'paddingButton': '25px',
        'height': 'auto'
    },

    'submit_button': {
        'background': '#119dff8c',
        'width': '90%',
        'margin': 'auto',
        'boxShadow': '3px 3px 3px rgb(0 106 181 / 55 %)'
    },

    'filter_button': {
        'background': '#119dff8c',
        'width': '74%',
        'margin': 'auto',
        'textAlign': 'left',
        'paddingLeft': '10px',
        'height': '35px',
        'fontSize': '8px'
    },

    # chart and table
    'chart': {
        'width': '94vh',
        'height': '64vh',
        'paddingTop': '40px',
    },

    'radio': {
        'display': 'flex',
        'float': 'right',
        'paddingTop': '10px',
        'fontSize': '14px'
    },

    'table': {
        'width': '100%',
        'padding': '40px',
        'fontSize': '14px'
    },

    # Tabs
    'main_tab_style': {
        'display': 'block',
        'width': '65%',
        'float': 'right',
        'background': '#f9f9f9',
        'boxShadow': '6px 6px 6px lightgray'
    },

    'tab_style': {
        'borderBottom': '1px solid transparent',
        'borderTop': '1px solid transparent',
        'padding': '6px',
        'backgroundColor': 'transparent',
        'borderLeft': '1px solid #d6d6d6',
        'borderRight': '1px solid #d6d6d6'

    },

    'tab_selected_style': {
        'borderTop': '1px solid #d6d6d6',
        'borderBottom': '1px solid #d6d6d6',
        'backgroundColor':  '#119dff8c',
        'color': 'black',
        'padding': '6px',
        'borderLeft': '1px solid #d6d6d6',
        'borderRight': '1px solid #d6d6d6'
    },

    'tab_content_style': {
        'margin': 'auto',
        'height': '69vh',
        'width': '95vh',
        'overflow': 'auto'
    },

    'mini_tab_style': {
        'paddingRight': '30px',
        'paddingLeft': '30px',
        'paddingBottom': '15px'
    }

}
