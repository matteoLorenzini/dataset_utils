<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html" indent="yes" encoding="UTF-8" />

  <xsl:template match="/">
    <html>
      <head>
        <title>OAI-PMH Response</title>
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; }
          h1 { color: #333; }
          table { border-collapse: collapse; width: 100%; }
          th, td { border: 1px solid #ddd; padding: 8px; }
          th { background-color: #f2f2f2; text-align: left; }
        </style>
      </head>
      <body>
        <h1>OAI-PMH Response</h1>
        <xsl:apply-templates />
      </body>
    </html>
  </xsl:template>

  <xsl:template match="*">
    <table>
      <tr>
        <th>Element</th>
        <th>Value</th>
      </tr>
      <xsl:for-each select="*">
        <tr>
          <td><xsl:value-of select="name()" /></td>
          <td><xsl:apply-templates /></td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>
</xsl:stylesheet>