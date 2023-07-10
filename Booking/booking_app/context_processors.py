from django.contrib.sites.shortcuts import get_current_site

def site_global_temp_var(request=None):
    site_id = get_current_site(request).id
    if site_id == 2: # uralholidays.com
        return {
            "contact_phone": "+8801600360071",
            "contact_email": "contact@uralholidays.com",
            "contact_address": "234/1 New elephant road, Katabon Signal, Dhaka 1205",
            "ssl_seal_html": """
                <!-- Begin DigiCert site seal HTML and JavaScript -->
                <script type='text/javascript'>
                    var __dcid = __dcid || [];__dcid.push(['DigiCertClickID_B1Qtj8n7', '15', 'l', 'black', 'B1Qtj8n7']);(function(){var cid=document.createElement('script');cid.async=true;cid.src='https://seal.digicert.com/seals/cascade/seal.min.js';var s = document.getElementsByTagName('script');var ls = s[(s.length - 1)];ls.parentNode.insertBefore(cid, ls.nextSibling);}());
                </script>
                <div style='display: flex; flex-direction: row; justify-content: space-between; width: 100%'>
                    <div id='DigiCertClickID_B1Qtj8n7' data-language='en'>
                    </div>
                    <div style='width: 90px'>
                        <img src='/static/images/iata.png' alt='iata' />
                    </div>
                </div>
                <!-- End DigiCert site seal HTML and JavaScript -->
            """,
            "google_gtag_html": """
                <!-- Global site tag (gtag.js) - Google Analytics -->
                <script async src="https://www.googletagmanager.com/gtag/js?id=G-SYQ3GVYRWR"></script>
                <script>
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());

                gtag('config', 'G-SYQ3GVYRWR');
                </script>
                <!-- End Global site tag (gtag.js) - Google Analytics -->
            """
        }
    elif site_id == 3: # uralholidays.co.uk
        return {
            "contact_phone": "+447441442558",
            "contact_email": "contact@uralholidays.co.uk",
            "contact_address": "Kemp House 160 City Road. London, EC1V 2NX",
            "ssl_seal_html": """
                <!-- Begin DigiCert site seal HTML and JavaScript -->
                <script type='text/javascript'>
                    var __dcid = __dcid || [];__dcid.push(['DigiCertClickID_AqmSGWce', '15', 'm', 'black', 'AqmSGWce']);(function(){var cid=document.createElement('script');cid.async=true;cid.src='https://seal.digicert.com/seals/cascade/seal.min.js';var s = document.getElementsByTagName('script');var ls = s[(s.length - 1)];ls.parentNode.insertBefore(cid, ls.nextSibling);}());
                </script>
                <div style='display: flex; flex-direction: row; justify-content: space-between; width: 100%'>
                    <div id='DigiCertClickID_AqmSGWce' data-language='en'>
                    </div>
                    <div style='width: 90px'>
                        <img src='/static/images/iata.png' alt='iata' />
                    </div>
                </div>

                <!-- End DigiCert site seal HTML and JavaScript -->
            """,
            "google_gtag_html": """
            <!-- Global site tag (gtag.js) - Google Analytics -->
            <script async src="https://www.googletagmanager.com/gtag/js?id=UA-216015553-1">
            </script>
            <script>
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());

                gtag('config', 'UA-216015553-1');
            </script>
            <!-- End Global site tag (gtag.js) - Google Analytics -->
            """
        }
    else:
        return {
            "contact_phone": "+8801611384371",
            "contact_email": "contact@uralholidays.com",
            "contact_address": "234/1 new elephant road,Dhaka 1205",
            "ssl_seal_html": """
                <div>Here SSL Seal Logo</div>
            """
        }
