<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<!--<xsl:import href="http://localhost:8082/static/content/web_viewer.xsl"/>-->
<xsl:import href="web_viewer.xsl"/>
<xsl:output method="html" />

<!--
<xsl:template match="/">
  <xsl:apply-templates />
</xsl:template>
-->

<xsl:template match="/graphtool">
  <!-- Start document layout. -->
  <!--<html xmlns="http://www.w3.org/1999/xhtml">-->
  <html>
    <head>
      <!-- Determine base URL for this document -->
      <xsl:variable name="static_base_url" select="query/attr[@name='static_base_url']" />
      <title> Results of Query: <xsl:value-of select="query/title"/> </title>
      
      <!-- Import the stylesheets for this document -->
      <!--
      <link rel="stylesheet" href="/static/content/style.css" type="text/css">
        <xsl:attribute name="href"> <xsl:value-of select="$static_base_url"/>/style.css </xsl:attribute>
      </link>
      -->
      <link rel="stylesheet" type="text/css" href="/static/content/reset-fonts-grids/reset-fonts-grids.css"/>

      <!-- Import the tooltip library -->
      <!--
      <script type="text/javascript" src="/static/content/wz_tooltip.js">
        <xsl:attribute name="src"> <xsl:value-of select="$static_base_url"/>/wz_tooltip.js </xsl:attribute>
      </script>
      -->
    
<link rel="stylesheet" type="text/css" href="/static/content/fonts/fonts-min.css" />
<link rel="stylesheet" type="text/css" href="/static/content/button/assets/skins/sam/button.css" />
<link rel="stylesheet" type="text/css" href="/static/content/container/assets/skins/sam/container.css" />
<link rel="stylesheet" type="text/css" href="/static/content/calendar/assets/skins/sam/calendar.css" />
<script type="text/javascript" src="/static/content/utilities/utilities.js"></script>
<script type="text/javascript" src="/static/content/button/button.js"></script>
<script type="text/javascript" src="/static/content/calendar/calendar.js"></script>
 
      <!-- TODO: figure out necessary additional YUI stuff -->
      <!-- Import things necessary for menu items -->
      <!-- Core + Skin CSS -->
      <link rel="stylesheet" type="text/css" href="/static/content/menu/assets/skins/sam/menu.css" />
      <!--<link rel="stylesheet" type="text/css" href="/static/content/container/assets/container.css" />-->

      <!-- Dependencies --> 
      <script type="text/javascript" src="/static/content/yahoo-dom-event/yahoo-dom-event.js"></script>
      <script type="text/javascript" src="/static/content/container/container_core-min.js"></script>
      <script type="text/javascript" src="/static/content/animation/animation-min.js"></script>
      
      <!-- Source File -->
      <script type="text/javascript" src="/static/content/menu/menu-min.js"></script>
      <script type="text/javascript" src="/static/content/container/container-min.js"></script>
      
      <!-- TODO: Import site header here. --> 
      <!--
      <xsl:call-template name="site_header">
          <xsl:with-param select="custom_head" />
      </xsl:call-template>
      -->
      <!-- TODO: do we need any additional parameters?  Query ought to be able to 
           inject arbitrary stuff, no? -->

<style type="text/css">
    /* Clear calendar's float */
    #container .bd:after {content:".";display:block;clear:left;height:0;visibility:hidden;}

    /* Have calendar squeeze upto bd bounding box */
    #container .bd {padding:0;}

    /* Remove calendar's border and set padding in ems instead of px, so we can specify an width in ems for the container */
    #cal {border:none;padding:1em}

    /* Datefield look/feel */
    .datefield {
        position:relative;
        top:10px;
        left:10px;
        white-space:nowrap;
        border:1px solid black;
        background-color:#eee;
        width:25em;
        padding:5px;
    }

    .datefield input,
    .datefield button,
    .datefield label  {vertical-align:middle}

    .datefield label  {font-weight:bold}
    .datefield input  {width:15em}
    .datefield button  {padding:0 5px 0 5px; margin-left:2px;}
    .datefield button img {padding:0;margin:0;vertical-align:middle}

    /* Example box */
    .box {
	position:relative;
    }
</style>

    </head>

    <body class="yui-skin-sam">
        <!--<xsl:call-template name="cms_mast"/>--> 
        <!--
        <xsl:call-template name="header">
            <xsl:with-param name="title" select="title" />
        </xsl:call-template>
        -->
        <xsl:call-template name="navtree">
            <xsl:with-param name="base_url" select="query/attr[@name='base_url']"/>
        </xsl:call-template>
        <xsl:apply-imports/>
    </body>
</html>

</xsl:template>

<xsl:template name="navtree">
<xsl:param name="base_url"/>

    <script type="text/javascript">
        // Initialize and render the menu bar when it is available in the DOM
        YAHOO.util.Event.onContentReady("navmenu", function () {

        // Instantiate and render the menu bar
        var oMenuBar = new YAHOO.widget.MenuBar("navmenu", { autosubmenudisplay: true, hidedelay: 750, lazyload: true });
        oMenuBar.render();

        });
    </script>

    <div id="navmenu" class="yuimenubar yuimenubarnav">
        <div class="bd">
            <ul class="first-of-type">
                <xsl:for-each select="document($base_url)/graphtool/pagelist">
                    <li class="yuimenubaritem"><a class="yuimenubaritemlabel" href="#navtree{@id}"><xsl:value-of select="@name"/></a>
                        <div id="navtree{@id}" class="yuimenu"> <div class="bd"> <ul>
                            <xsl:for-each select="page">
                                <li class="yuimenuitem">
                                    <xsl:choose>
                                        <xsl:when test="@title">
                                            <a class="yuimenuitemlabel" href="{.}"><xsl:value-of select="@title" /></a>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <a class="yuimenuitemlabel" href="{.}"><xsl:value-of select="." /></a>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </li>
                            </xsl:for-each>
                        </ul></div></div>
                    </li>
                </xsl:for-each>
            </ul>
        </div>
    </div>
</xsl:template>

<!-- TODO: add the CMS mast here. -->
<!--
<xsl:template name="cms_mast"/>
-->

<!-- TODO: add header here. -->
<!--
<xsl:template name="header"/>
-->

</xsl:stylesheet>
