<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

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

<xsl:template match="query">
    <xsl:variable name="static_base_url" select="attr[@name='static_base_url']" />
    <xsl:choose>
        <xsl:when test="graph">
          <xsl:if test="data/@coords">
            <xsl:variable name="pivot_name" select="data/@pivot" />
            <xsl:variable name="group_name" select="data/@group" />
            <p> <img usemap="#map" src="{url}"/> </p>
            <xsl:variable name="kind" select="data/@kind"/> 
            <xsl:variable name="my_columns" select="columns" />
            <map id="graph_map"> </map>
            <script>
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
            </script>
          </xsl:if>
          <xsl:if test="not(data/@coords)">
            <p> <img src="{url}"/> </p>
          </xsl:if> 
        </xsl:when>
        <xsl:otherwise>
            <h1> <xsl:value-of select="title"/> </h1>
        </xsl:otherwise>
    </xsl:choose>

    <h3 style="text-align:left;"> Variables </h3>
    <form method="get" action="{@name}">

        <xsl:for-each select="sqlvars/var">
            <xsl:choose>
                <xsl:when test="@name='time' or @name='starttime' or @name='endtime'">
                <!--<xsl:when test="@name='endtime'">-->

<!--BEGIN SOURCE CODE FOR CALENDAR =============================== -->
<script type="text/javascript">
    YAHOO.util.Event.onDOMReady(function(){

        var dialog_<xsl:value-of select="@name"/>, calendar_<xsl:value-of select="@name"/>;

        calendar_<xsl:value-of select="@name"/> = new YAHOO.widget.Calendar("cal-<xsl:value-of select="@name"/>", {
            iframe:false,          // Turn iframe off, since container has iframe support.
            hide_blank_weeks:true  // Enable, to demonstrate how we handle changing height, using changeContent
        });

        function okHandler() {
            if (calendar_<xsl:value-of select="@name"/>.getSelectedDates().length > 0) {
                var selDate = calendar_<xsl:value-of select="@name"/>.getSelectedDates()[0];
                var dStr = selDate.getDate();
                var mStr = selDate.getMonth()+1;
                var yStr = selDate.getFullYear();

                YAHOO.util.Dom.get("date-<xsl:value-of select="@name"/>").value = yStr + "-" + mStr + "-" + dStr + " 00:00:00";
            } else {
                YAHOO.util.Dom.get("date-<xsl:value-of select="@name"/>").value = "";
            }
            this.hide();
        }
        
        function cancelHandler() {
            this.hide();
        }

        dialog_<xsl:value-of select="@name"/> = new YAHOO.widget.Dialog("container-<xsl:value-of select="@name"/>", {
            context:["show-<xsl:value-of select="@name"/>", "tl", "bl"],
            buttons:[ {text:"Select", isDefault:true, handler: okHandler}, 
                      {text:"Cancel", handler: cancelHandler}],
            width:"16em",
            draggable:false,
            close:true
        });
        calendar_<xsl:value-of select="@name"/>.render();
        dialog_<xsl:value-of select="@name"/>.render();

        // Using dialog.hide() instead of visible:false is a workaround for an IE6/7 container known issue with border-collapse:collapse.
        dialog_<xsl:value-of select="@name"/>.hide();

        calendar_<xsl:value-of select="@name"/>.renderEvent.subscribe(function() {
            // Tell Dialog it's contents have changed, Currently used by container for IE6/Safari2 to sync underlay size
            dialog_<xsl:value-of select="@name"/>.fireEvent("changeContent");
        });

        YAHOO.util.Event.on("show-<xsl:value-of select="@name"/>", "click", dialog_<xsl:value-of select="@name"/>.show, dialog_<xsl:value-of select="@name"/>, true);
    });
</script>

<div class="box">
    <div class="datefield">
        <label for="date"><xsl:value-of select="@name"/>: </label>
        <input type="text" id="date-{@name}" name="{@name}" value="{.}" />
        <button type="button" id="show-{@name}" title="Show Calendar">
            <img src="/static/content/calbtn.gif" width="18" height="18" alt="Calendar">
                <xsl:attribute name="src"><xsl:value-of select="$static_base_url"/>/calbtn.gif</xsl:attribute>
            </img>
        </button>
    </div>
    <div id="container-{@name}">
        <div class="hd">Calendar</div>
        <div class="bd">
            <div id="cal-{@name}"></div>
        </div>
    </div>
</div>

<!--END SOURCE CODE FOR CALENDAR =============================== -->
                </xsl:when>
                <xsl:when test="@name='span'">
<!--START SOURCE CODE FOR SPAN ================================= -->
<script type="text/javascript">
    YAHOO.example.init = function () {

        // "contentready" event handler for the "menubuttonsfrommarkup" <fieldset>
        YAHOO.util.Event.onContentReady("menubuttonsfrommarkup", function () {

            // Create a Button using an existing <input> element as a data source
            var oMenuButton1 = new YAHOO.widget.Button("menubutton1", { type: "menu", menu: "menubutton1select" });
            var oMenuButton2 = new YAHOO.widget.Button("menubutton2", { type: "menu", menu: "menubutton2select" });

            // Create a Button using an existing <input> element and a YAHOO.widget.Overlay instance as its menu
            var oMenuButton3 = new YAHOO.widget.Button("menubutton3", { type: "menu", menu: "menubutton3menu" });
        
        });

        // "click" event handler for each item in the Button's menu
        function onMenuItemClick(p_sType, p_aArgs, p_oItem) {
            oMenuButton4.set("label", p_oItem.cfg.getProperty("text"));
        }


        // Create a Button without using existing markup
        //  Create an array of YAHOO.widget.MenuItem configuration properties
        var aMenuButton4Menu = [
            { text: "one", value: 1, onclick: { fn: onMenuItemClick } },
            { text: "two", value: 2, onclick: { fn: onMenuItemClick } },
            { text: "three", value: 3, onclick: { fn: onMenuItemClick } }
        ];

        /*
            Instantiate a Menu Button using the array of YAHOO.widget.MenuItem 
            configuration properties as the value for the "menu" configuration 
            attribute.
        */
        var oMenuButton4 = new YAHOO.widget.Button({ type: "menu", label: "one", name: "mymenubutton", menu: aMenuButton4Menu, container: "menubuttonsfromjavascript" });            


        /*
            Search for an element to place the Menu Button into via the 
            Event utilities "onContentReady" method
        */
        
        YAHOO.util.Event.onContentReady("menubuttonsfromjavascript", function () {
            // Instantiate an Overlay instance
            var oOverlay = new YAHOO.widget.Overlay("menubutton5menu", { visible: false });
            oOverlay.setBody("Menu Button 5 Menu");
            // Instantiate a Menu Button
            var oMenuButton5 = new YAHOO.widget.Button({ type: "menu", label: "Menu Button 5", menu: oOverlay });
            /*
                 Append the Menu Button and Overlay to the element with the id 
                 of "menubuttonsfromjavascript"
            */
            oMenuButton5.appendTo(this);
            oOverlay.render(this);
        });

        function onExampleSubmit(p_oEvent) {
            var bSubmit = window.confirm("Are you sure you want to submit this form?");
            if(!bSubmit) {
                YAHOO.util.Event.preventDefault(p_oEvent);
            }
        }
        YAHOO.util.Event.on("button-example-form", "submit", onExampleSubmit);

    } ();

</script>
<input type="submit" id="menubutton1" name="menubutton1_button" value="Menu Button 1">
<select id="menubutton1select" name="menubutton1select">
    <option value="0">One</option>
    <option value="1">Two</option>
    <option value="2">Three</option>                
</select>

<!--END SOURCE CODE FOR SPAN =================================== -->
                </xsl:when>
                <xsl:otherwise>
                    <div class="datefield">
                        <label> <xsl:value-of select="@name"/>: </label>
                        <input type="text" name="{@name}" value="{.}" /> 
                    </div>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each><br/>
        <p style="text-align:left;"><input type="submit" value="Query again"/></p>
    </form>
    
<!--
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
-->

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

</xsl:stylesheet>
