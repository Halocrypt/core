EMAIL_CONFIRMATION_TEMPLATE = """<!DOCTYPE html>
<html>
  <body
    style="
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
        Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    "
  >
    <table style="border-collapse: collapse; border-spacing: 0">
      <tr>
        <td style="border: 10px solid transparent">
          Hey, did you request an email confirmation?
        </td>
      </tr>
      <tr>
        <td style="border: 10px solid transparent">
          <a href="{url}">confirm your email address</a>
        </td>
      </tr>
      <tr>
        <td style="border: 10px solid transparent">Team Halocrypt</td>
      </tr>
    </table>
  </body>
</html>
"""


PASSWORD_RESET_TEMPLATE = """<!DOCTYPE html>
<html>
  <body
    style="
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
        Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    "
  >
    <table style="border-collapse: collapse; border-spacing: 0">
      <tr>
        <td style="border: 10px solid transparent">
          Our records indicate that you requested a password reset
        </td>
      </tr>
      <tr>
        <td style="border: 10px solid transparent">
          <a href="{url}">Click here to set a new password</a>
        </td>
      </tr>
      <tr>
        <td style="border: 10px solid transparent">
          If that wasn't you, feel free to ignore this email
        </td>
      </tr>
      <tr>
        <td style="border: 10px solid transparent">Team Halocrypt</td>
      </tr>
    </table>
  </body>
</html>
"""
