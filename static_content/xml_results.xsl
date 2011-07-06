<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html" />

<xsl:template match="/">
  <xsl:apply-templates />
</xsl:template>

<xsl:template name="split-text">
<xsl:param name="arg1"/>
<xsl:choose>
<xsl:when test="contains($arg1,'&#10;')">
<xsl:value-of select="substring-before($arg1,'&#10;')"/><br/>
<xsl:call-template name="split-text">
<xsl:with-param name="arg1">
<xsl:value-of select="substring-after($arg1,'&#10;')"/>
</xsl:with-param>
</xsl:call-template>
</xsl:when>
<xsl:otherwise>
<xsl:value-of select="$arg1"/>
</xsl:otherwise>
</xsl:choose>
</xsl:template>

<xsl:template match="/graphtool/query">
  <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
      <xsl:variable name="static_base_url" select="attr[@name='static_base_url']" />
      <title> Results of Query: <xsl:value-of select="title"/> </title>
      <link rel="stylesheet" href="/static/content/style.css" type="text/css">
        <xsl:attribute name="href"> <xsl:value-of select="$static_base_url"/>/style.css </xsl:attribute>
      </link>
      <script type="text/javascript" src="/static/content/wz_tooltip.js">
        <xsl:attribute name="src"> <xsl:value-of select="$static_base_url"/>/wz_tooltip.js </xsl:attribute>
      </script>
      <script type="text/javascript">
          function toggleBox( divId, state ) {
            var obj = document.getElementById( divId ).style;
            obj.visibility = state ? "visible" : "hidden";
            obj.display = state ? "block" : "none";
          }

          function toggleBoxSwitch( divId, state ) {
            var obj = document.getElementById( divId ).style;
            if (state == 2) {
                if (obj.visibility == "visible")
                    obj.visibility = "hidden";
                else
                    obj.visibility = "visible";
            } else 
                obj.visibility = state ? "visible" : "hidden";
          }

          function testAlert( arg ) { alert( arg ); }
      </script>
    </head>
    <body onLoad="tt_Init();">
      <xsl:call-template name="navtree">
          <xsl:with-param name="base_url" select="attr[@name='base_url']" />
      </xsl:call-template>
      <xsl:choose>
        <xsl:when test="graph">
          <xsl:if test="data/@coords">
            <xsl:variable name="pivot_name" select="data/@pivot" />
            <xsl:variable name="group_name" select="data/@group" />
            <p> <img usemap="#map" src="{url}"/> </p>
            <xsl:variable name="kind" select="data/@kind"/> 
            <xsl:variable name="my_columns" select="columns" />
            <map name="map">
              <xsl:for-each select="data/*">
                <xsl:variable name="my_pivot">
                <xsl:choose>
                  <xsl:when test="$pivot_name='Link_false'"> <xsl:value-of select="@from" /> to <xsl:value-of select="@to" /> </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="@name" />
                  </xsl:otherwise>
                </xsl:choose>
                </xsl:variable>
                <xsl:choose>
                  <xsl:when test="$kind='pivot-group'">
                    <xsl:for-each select="group">
                      <xsl:if test="coords">
                        <xsl:variable name="my_data" select="d"/>
                        <xsl:variable name="mouseover_data">
                          return escape('&lt;b&gt;<xsl:value-of select="$pivot_name"/>:&lt;/b&gt; <xsl:value-of select="$my_pivot"/> &lt;br/&gt; &lt;b&gt; <xsl:value-of select="$group_name"/>: &lt;/b&gt; <xsl:value-of select="@value" /> &lt;br/&gt; <xsl:for-each select="$my_columns/*"> <xsl:variable name="index" select="@index" /> &lt;b&gt; <xsl:value-of select="." />:&lt;/b&gt; <xsl:value-of select="$my_data[position()=$index]" /><xsl:if test="string-length(@unit) > 0">&#160;<xsl:value-of select="@unit" /> </xsl:if> &lt;br/&gt; </xsl:for-each>');
                        </xsl:variable>
                        <!--<p> <xsl:value-of select="$mouseover_data" /> </p>-->
                        <area href="#" shape="poly" onClick="return false;">
                          <xsl:attribute name="coords"> <xsl:value-of select="coords"/> </xsl:attribute>
                          <xsl:attribute name="onMouseOver"> <xsl:value-of select="$mouseover_data" /> </xsl:attribute>
                        </area>
                      </xsl:if>
                    </xsl:for-each>
                  </xsl:when>
                  <xsl:when test="($kind='pivot') and (coords)">
                    <xsl:variable name="my_data" select="d" />
                    <xsl:variable name="mouseover_data">
                      return escape('&lt;b&gt;<xsl:value-of select="$pivot_name"/>:&lt;/b&gt; <xsl:value-of select="$my_pivot"/> &lt;br/&gt; <xsl:for-each select="$my_columns/*"> <xsl:variable name="index" select="@index" /> &lt;b&gt; <xsl:value-of select="." />:&lt;/b&gt; <xsl:value-of select="$my_data[position()=$index]" /><xsl:if test="string-length(@unit) > 0">&#160;<xsl:value-of select="@unit" /> </xsl:if> &lt;br/&gt; </xsl:for-each>');
                    </xsl:variable>
                    <area href="#" shape="poly" onClick="return false;">
                          <xsl:attribute name="coords"> <xsl:value-of select="coords"/> </xsl:attribute>
                          <xsl:attribute name="onMouseOver"> <xsl:value-of select="$mouseover_data" /> </xsl:attribute>
                    </area>
                  </xsl:when>
                </xsl:choose>
              </xsl:for-each>
            </map>
          </xsl:if>
          <xsl:if test="not(data/@coords)">
            <p> <img src="{url}"/> </p>
          </xsl:if> 
        </xsl:when>
        <xsl:otherwise>
          <h1> <xsl:value-of select="title"/> </h1>
        </xsl:otherwise>
      </xsl:choose>

      <h3> Variables </h3>
      <form method="get" action="{@name}">
        <table border="1">
          <thead>
            <tr>
              <th> Name </th>
              <th> Value </th>
            </tr>
          </thead>
          <xsl:for-each select="sqlvars/var">
            <tr>
              <td> <xsl:value-of select="@name" /> </td>
              <td> <input type="text" name="{@name}" value="{.}" /> </td>
            </tr>
          </xsl:for-each>
        </table>
        <input type="submit" value="Query again"/>
      </form>

      <xsl:variable name="csv_url" select="concat(translate(attr[@name='base_url'], 'xml', 'csv'), '/', @name, '?', substring-after(url, '?'))"/>
      <a href="{$csv_url}">Download results in CSV format</a>

      <div id="metadata_button" class="test" style="visibility:visible;">
        <a href="#" onClick="toggleBox('metadata',1); toggleBox('metadata_button',0); return false;">Show metadata</a>
      </div>
      <div id="metadata" class="test" style="visibility:hidden;display:none">
        <xsl:if test="graph">
          <p>Graph Type: <xsl:value-of select="graph"/></p>
        </xsl:if>
        <p>
          <h3>SQL Used:</h3>
          <xsl:call-template name="split-text">
            <xsl:with-param name="arg1">
              <xsl:value-of select="sql"/>
            </xsl:with-param>
          </xsl:call-template>
        </p>
        <a href="#" onClick="toggleBox('metadata',0); toggleBox('metadata_button',1); return false;">Hide metadata</a>
      </div>

 
      <div id="results_button" class="test">
        <xsl:attribute name="style">
          <xsl:choose>
            <xsl:when test="graph"> visibility:visible; </xsl:when>
            <xsl:otherwise> visibility:hidden; </xsl:otherwise>
          </xsl:choose>
        </xsl:attribute>
        <a href="#" onClick="toggleBox('results',1); toggleBox('results_button',0); return false;">Show table of results</a>
      </div>

      <div id="results" class="test">

        <xsl:attribute name="style">
          <xsl:choose>
            <xsl:when test="graph"> visibility:hidden; display:none </xsl:when>
            <xsl:otherwise> visibility:visible; </xsl:otherwise>
          </xsl:choose>
        </xsl:attribute>

      <h3> Table of Results </h3>
      <table border="1">
        <thead>
          <tr>
            <th> <xsl:value-of select="data/@pivot" /> </th>
            <xsl:if test="data/@kind='pivot-group'">
              <th> <xsl:value-of select="data/@group" /> </th>
            </xsl:if>
            <xsl:for-each select="columns/column">
              <th>
                <xsl:value-of select="." />
                <xsl:if test="string-length(@unit) > 0"> (<xsl:value-of select="@unit" />) </xsl:if>
              </th>
            </xsl:for-each>
          </tr>
        </thead>
        <xsl:variable name="pivot_name" select="data/@pivot" />
        <xsl:variable name="group_name" select="data/@group" />
        <tbody>
          <xsl:if test="data/@kind='pivot-group'">
            <xsl:for-each select="data/*"> 
              <xsl:variable name="my_pivot">
                <xsl:choose>
                  <xsl:when test="$pivot_name='Link_false'">
                      <xsl:value-of select="@from" />
                      to
                      <xsl:value-of select="@to" />
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="@name" />
                  </xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
              <xsl:for-each select="group" >
                <tr>
                  <td> <xsl:value-of select="$my_pivot" /> </td>
                  <td> <xsl:value-of select="@value" /> </td>
                  <xsl:for-each select="d">
                    <td> 
                      <xsl:call-template name="split-text">
                        <xsl:with-param name="arg1">
                          <xsl:value-of select="."/>
                        </xsl:with-param>
                      </xsl:call-template>
                    </td>
                  </xsl:for-each>
                </tr>
	      </xsl:for-each>
            </xsl:for-each>
          </xsl:if>
          <xsl:if test="data/@kind='pivot'">
            <xsl:for-each select="data/*">
              <xsl:variable name="my_pivot">
                <xsl:choose>
                  <xsl:when test="$pivot_name='Link_false'">
                      <xsl:value-of select="@from" />
                      to
                      <xsl:value-of select="@to" />
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="@name" />
                  </xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
                <tr>
                  <td> <xsl:value-of select="$my_pivot" /> </td>
                  <xsl:for-each select="d">
                    <td>
                      <xsl:call-template name="split-text">
                        <xsl:with-param name="arg1">
                          <xsl:value-of select="."/>
                        </xsl:with-param>
                      </xsl:call-template>
                  </td>
                  </xsl:for-each>
                </tr>
            </xsl:for-each>
          </xsl:if>
        </tbody>
      </table>

      <a href="#" onClick="toggleBox('results',0); toggleBox('results_button',1); return false;">Hide table of results</a>

      </div>

    </body>
  </html>
</xsl:template>

<xsl:template match="/graphtool/pagelist">

<html>
  <head>
    <title> <xsl:value-of select="@name" /> </title>
  </head>
  <body>
    <h1> <xsl:value-of select="@name" /> </h1>
    <ul>
      <xsl:for-each select="page">
        <xsl:choose>
          <xsl:when test="@title">
            <li> <a href="{.}"><xsl:value-of select="@title" /></a> </li>
          </xsl:when>
          <xsl:otherwise>
            <li> <a href="{.}"><xsl:value-of select="." /></a> </li>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
    </ul>
  </body>
</html>

</xsl:template>

<xsl:template name="navtree">
  <xsl:param name="base_url" />
  <xsl:for-each select="document($base_url)/graphtool/pagelist">

    <!--<div class="menu" onClick="toggleBoxSwitch('navmenu',2);" onMouseOver="toggleBoxSwitch('navmenu',1);" onMouseOut="toggleBoxSwitch('navmenu',0)"> -->
    <div class="menu">
      <xsl:attribute name="onClick">toggleBoxSwitch('navmenu<xsl:value-of select="@id"/>',2);</xsl:attribute>
      <!--<xsl:attribute name="onMouseOver">toggleBoxSwitch('navmenu<xsl:value-of select="@id"/>',1);</xsl:attribute>
      <xsl:attribute name="onMouseOut">toggleBoxSwitch('navmenu<xsl:value-of select="@id"/>',0)</xsl:attribute>-->
      <xsl:attribute name="style"> left:<xsl:value-of select="(200*@id)-200" />px; </xsl:attribute>
      <a href="#" onClick="return false;"> <xsl:value-of select="@name"/> </a>
    </div>

    <!--<div class="menuopt" id="navmenu" onMouseOut="toggleBoxSwitch('navmenu',0)" onMouseOver="toggleBoxSwitch('navmenu',1)">-->
    <div class="menuopt">
      <xsl:attribute name="id">navmenu<xsl:value-of select="@id"/></xsl:attribute>
      <!--<xsl:attribute name="onMouseOut">toggleBoxSwitch('navmenu<xsl:value-of select="@id"/>',0)</xsl:attribute>
      <xsl:attribute name="onMouseOut">toggleBoxSwitch('navmenu<xsl:value-of select="@id"/>',1)</xsl:attribute>-->
      <xsl:attribute name="style">left:<xsl:value-of select="(200*@id)-200" />px;</xsl:attribute>
      <ul>
        <xsl:for-each select="page">
          <xsl:choose>
            <xsl:when test="@title">
              <li> <a href="{.}"><xsl:value-of select="@title" /></a> </li>
            </xsl:when>
            <xsl:otherwise>
              <li> <a href="{.}"><xsl:value-of select="." /></a> </li>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:for-each>
      </ul>
    </div>

  </xsl:for-each>

</xsl:template>

</xsl:stylesheet>
