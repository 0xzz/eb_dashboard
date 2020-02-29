import dash
import os

_default_index = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

_app_entry = """
<div id="react-entry-point">
    <div class="_dash-loading">
        Loading...
    </div>
</div>
"""

class CustomIndexDash(dash.Dash):
    """Custom Dash class overriding index() method for local CSS support"""
    def _generate_google_ads_html(self, html_path=''):
        google_ads_str = ''
        if html_path and os.path.isfile(html_path):
            with open(html_path,'r') as f:
                google_ads_str = f.readline()
        return google_ads_str

    def _format_tag(self, tag_name, attributes, inner="", closed=False, opened=False):
        tag = "<{tag} {attributes}"
        if closed:
            tag += "/>"
        elif opened:
            tag += ">"
        else:
            tag += ">" + inner + "</{tag}>"
        return tag.format(
            tag=tag_name,
            attributes=" ".join(
                ['{}="{}"'.format(k, v) for k, v in attributes.items()]
            ),
        )

    def index(self, *args, **kwargs):  # pylint: disable=unused-argument
        ad_js_loc = os.path.join(self.config.assets_folder, 'ads.html')
        adsense_js = self._generate_google_ads_html(ad_js_loc)

        scripts = self._generate_scripts_html()
        css = self._generate_css_dist_html()
        config = self._generate_config_html()
        metas = self._generate_meta_html()
        
        renderer = self._generate_renderer()
        title = getattr(self, "title", "Dash")
        title += ('\n'+adsense_js)

        if self._favicon:
            favicon_mod_time = os.path.getmtime(
                os.path.join(self.config.assets_folder, self._favicon)
            )
            favicon_url = self.get_asset_url(self._favicon) + "?m={}".format(
                favicon_mod_time
            )
        else:
            favicon_url = "{}_favicon.ico?v={}".format(
                self.config.requests_pathname_prefix, '1.9.0'#__version__
            )

        favicon = self._format_tag(
            "link",
            {"rel": "icon", "type": "image/x-icon", "href": favicon_url},
            opened=True,
        )

        index = self.interpolate_index(
            metas=metas,
            title=title,
            css=css,
            config=config,
            scripts=scripts,
            app_entry=_app_entry,
            favicon=favicon,
            renderer=renderer,
        )

        # checks = (
        #     (_re_index_entry_id.search(index), "#react-entry-point"),
        #     (_re_index_config_id.search(index), "#_dash-configs"),
        #     (_re_index_scripts_id.search(index), "dash-renderer"),
        #     (_re_renderer_scripts_id.search(index), "new DashRenderer"),
        # )
        # missing = [missing for check, missing in checks if not check]

        # if missing:
        #     plural = "s" if len(missing) > 1 else ""
        #     raise exceptions.InvalidIndexException(
        #         "Missing element{pl} {ids} in index.".format(
        #             ids=", ".join(missing), pl=plural
        #         )
        #     )

        return index