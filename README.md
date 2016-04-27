# AutoDocs for Confluence

Required:

    skytap (https://github.com/FulcrumIT/skytap, pip install it)
    skytapdns (https://github.com/FulcrumIT/skytapdns, put package folder into autodocs directory)
    pyconfluence (https://github.com/FulcrumIT/pyconfluence, pip install it)
    

To use, first set up config.yml with appropriate values as indicated in config_template.yml, and environment variables for skytap and pyconfluence.

Afterwards, from within the autodocs directory, run the following to update specific documentation:

Update all environment pages:

    python update.py write
    
Update India VPN environment page:

    python update.py india
    
Update VZW Published Services page:

    python update.py services
    
Update DNS Aliases page:

    python update.py aliases
