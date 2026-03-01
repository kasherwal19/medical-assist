hero = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .hero-section {
            background: linear-gradient(135deg, #e8eef5 0%, #f0f4f8 100%);
            padding: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .image-container {
            width: 100%;
            max-width: 600px;
            height: 400px;
            margin-bottom: 40px;
            border: 2px dashed #ccc;
            border-radius: 4px;
            overflow: hidden;
            background-color: #fff;
        }

        .image-container img {
            width: 100%;
            height: 100%;
            display: block;
            object-fit: cover;
        }

        .content-section {
            padding: 40px;
            background-color: #ffffff;
        }

        .content-title {
            font-size: 28px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 15px;
        }

        .content-text {
            color: #333;
            line-height: 1.8;
            font-size: 16px;
        }

        .content-text h2 {
            font-size: 22px;
            font-weight: 600;
            color: #1a1a1a;
            margin-top: 25px;
            margin-bottom: 15px;
            border-left: 4px solid #007bff;
            padding-left: 15px;
        }

        .content-text h3 {
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-top: 18px;
            margin-bottom: 12px;
            padding-left: 10px;
        }

        .content-text h4 {
            font-size: 16px;
            font-weight: 600;
            color: #34495e;
            margin-top: 15px;
            margin-bottom: 10px;
        }

        .content-text p {
            margin-bottom: 15px;
        }

        .content-text ol {
            margin-left: 20px;
            margin-bottom: 15px;
        }

        .content-text li {
            margin-bottom: 10px;
            color: #444;
        }

        .content-text ul {
            margin-left: 20px;
            margin-bottom: 15px;
        }

        .content-text ul li {
            margin-bottom: 8px;
            color: #444;
        }

        .content-text strong {
            color: #1a1a1a;
            font-weight: 600;
        }

        /* Special styled boxes */
        .highlight-box {
            background-color: #e7f3ff;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            color: #004085;
        }

        .evidence-gap {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            font-style: italic;
            color: #856404;
        }

        .warning-box {
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            color: #721c24;
        }

        .data-correction {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            color: #155724;
        }

        .section-divider {
            border: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, #ddd, transparent);
            margin: 25px 0;
        }

        /* Table styles */
        .table-wrapper {
            overflow-x: auto;
            margin: 20px 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }

        table th {
            background-color: #007bff;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }

        table td {
            border-bottom: 1px solid #ddd;
            padding: 12px;
        }

        table tr:hover {
            background-color: #f5f5f5;
        }

        .old-value {
            text-decoration: line-through;
            color: #999;
            font-size: 13px;
        }

        @media (max-width: 768px) {
            .hero-section {
                padding: 20px;
            }

            .content-section {
                padding: 20px;
            }

            .content-title {
                font-size: 22px;
            }

            .content-text {
                font-size: 14px;
            }
        }
    </style>
</head>

<body>
    <div class="container">
        <!-- Hero Section with Image -->
        <div class="hero-section">
            <div class="image-container">
                <img src="{image_url}" alt="Content Banner">
            </div>
        </div>

        <!-- Content Section -->
        <div class="content-section">
            <div class="content-text">
                {content}
            </div>
        </div>
    </div>
</body>

</html>"""


dual = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        /* Hero section with image - inspired by hero template */
        .hero-section {
            background: linear-gradient(135deg, #e8eef5 0%, #f0f4f8 100%);
            padding: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .image-container {
            width: 100%;
            max-width: 600px;
            height: 400px;
            margin-bottom: 40px;
            border: 2px dashed #ccc;
            border-radius: 4px;
            overflow: hidden;
            background-color: #fff;
        }

        .image-container img {
            width: 100%;
            height: 100%;
            display: block;
            object-fit: cover;
        }

        /* Content section with title and columns */
        .content-section {
            padding: 40px;
            background-color: #ffffff;
        }

        .content-title {
            font-size: 28px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 15px;
        }

        /* Two column layout */
        .columns {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-top: 25px;
        }

        .column {
            color: #333;
            line-height: 1.8;
            font-size: 16px;
        }

        .column h2 {
            font-size: 22px;
            font-weight: 600;
            color: #1a1a1a;
            margin-top: 25px;
            margin-bottom: 15px;
            border-left: 4px solid #007bff;
            padding-left: 15px;
        }

        .column h2:first-child {
            margin-top: 0;
        }

        .column h3 {
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-top: 18px;
            margin-bottom: 12px;
            padding-left: 10px;
        }

        .column h4 {
            font-size: 16px;
            font-weight: 600;
            color: #34495e;
            margin-top: 15px;
            margin-bottom: 10px;
        }

        .column p {
            margin-bottom: 15px;
        }

        .column ol {
            margin-left: 20px;
            margin-bottom: 15px;
        }

        .column li {
            margin-bottom: 10px;
            color: #444;
        }

        .column ul {
            margin-left: 20px;
            margin-bottom: 15px;
        }

        .column ul li {
            margin-bottom: 8px;
            color: #444;
        }

        .column strong {
            color: #1a1a1a;
            font-weight: 600;
        }

        /* Special styled boxes */
        .highlight-box {
            background-color: #e7f3ff;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            color: #004085;
        }

        .evidence-gap {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            font-style: italic;
            color: #856404;
        }

        .warning-box {
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            color: #721c24;
        }

        .data-correction {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            color: #155724;
        }

        .section-divider {
            border: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, #ddd, transparent);
            margin: 25px 0;
        }

        /* Table styles */
        .table-wrapper {
            overflow-x: auto;
            margin: 20px 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }

        table th {
            background-color: #007bff;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }

        table td {
            border-bottom: 1px solid #ddd;
            padding: 12px;
        }

        table tr:hover {
            background-color: #f5f5f5;
        }

        .old-value {
            text-decoration: line-through;
            color: #999;
            font-size: 13px;
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .hero-section {
                padding: 20px;
            }

            .content-section {
                padding: 20px;
            }

            .content-title {
                font-size: 22px;
            }

            .columns {
                grid-template-columns: 1fr;
                gap: 25px;
            }

            .column {
                font-size: 14px;
            }
        }
    </style>
</head>

<body>
    <div class="container">
        <div class="hero-section">
            <div class="image-container">
                <img src="{image_url_1}" alt="Content Banner">
            </div>
        </div>
        

        <!-- Content Section with Title and Two Columns -->
        <div class="content-section">

            <div class="columns">
                <div class="column">
                    {content_1}
                </div>
                <div class="column">
                    {content_2}
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""



embedded = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: #f5f5f5;
      padding: 20px;
    }

    .container {
      max-width: 900px;
      margin: 0 auto;
      background-color: white;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .top {
      padding: 36px 40px 0 40px;
      background: linear-gradient(135deg, #e8eef5 0%, #f0f4f8 100%);
      display: flex;
      flex-direction: column;
      align-items: flex-start;
    }

    .content-title {
      font-size: 28px;
      font-weight: 600;
      color: #1a1a1a;
      margin-bottom: 18px;
      padding-bottom: 12px;
      width: 100%;
    }

    /* Embedded area: image left, side content right */
    .embedded-area {
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 28px;
      width: 100%;
      margin-top: 18px;
    }

    .embedded-image {
      border: 2px dashed #ccc;
      border-radius: 4px;
      overflow: hidden;
      background: #fff;
      width: 100%;
      max-width: 320px;
            height: 320px;
    }
        .embedded-image img { width: 100%; height: 100%; display: block; object-fit: cover; }

    .side {
      color: #333;
      line-height: 1.8;
      font-size: 16px;
    }

    .side h2 {
      font-size: 22px;
      font-weight: 600;
      color: #1a1a1a;
      margin-top: 0;
      margin-bottom: 15px;
      border-left: 4px solid #007bff;
      padding-left: 15px;
    }

    .side h3 {
      font-size: 18px;
      font-weight: 600;
      color: #2c3e50;
      margin-top: 18px;
      margin-bottom: 12px;
    }

    .side p {
      margin-bottom: 15px;
    }

    .side ul, .side ol {
      margin-left: 20px;
      margin-bottom: 15px;
    }

    .side li {
      margin-bottom: 10px;
      color: #444;
    }

    /* below content continues full width under embedded area */
    .below {
      padding: 28px 40px 36px 40px;
      background: #ffffff;
      color: #333;
      line-height: 1.8;
      font-size: 16px;
    }
    
    .below h2 {
      font-size: 22px;
      font-weight: 600;
      color: #1a1a1a;
      margin-top: 0;
      margin-bottom: 15px;
      border-left: 4px solid #007bff;
      padding-left: 15px;
    }

    .below h3 {
      font-size: 18px;
      font-weight: 600;
      color: #2c3e50;
      margin-top: 18px;
      margin-bottom: 12px;
    }

    .below p { 
      margin-bottom: 15px;
    }

    .below ul, .below ol {
      margin-left: 20px;
      margin-bottom: 15px;
    }

    .below li {
      margin-bottom: 10px;
      color: #444;
    }

    /* boxes to match hero look */
    .highlight-box { background-color: #e7f3ff; border-left: 4px solid #007bff; padding: 12px; border-radius: 4px; margin: 12px 0; color: #004085; }
    .warning-box { background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 12px; border-radius: 4px; margin: 12px 0; color: #721c24; }
    .evidence-gap { background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; border-radius: 4px; margin: 12px 0; color: #856404; font-style: italic; }
    .data-correction { background-color: #d4edda; border-left: 4px solid #28a745; padding: 12px; border-radius: 4px; margin: 12px 0; color: #155724; }

    .section-divider {
      border: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, #ddd, transparent);
      margin: 25px 0;
    }

    /* Table styles */
    .table-wrapper { overflow-x: auto; margin: 20px 0; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    table th { background-color: #007bff; color: white; padding: 12px; text-align: left; font-weight: 600; }
    table td { border-bottom: 1px solid #ddd; padding: 12px; }
    table tr:hover { background-color: #f5f5f5; }
    .old-value { text-decoration: line-through; color: #999; font-size: 13px; }

    @media (max-width: 768px) {
      .embedded-area { grid-template-columns: 1fr; gap: 18px; }
      .top { padding: 20px; }
      .below { padding: 20px; }
      .content-title { font-size: 22px; }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="top">
      <div class="content-title">{title}</div>
    </div>
    <div class="embedded-area">
        <div class="embedded-image">
          <img src="{image_url}" alt="Embedded image">
        </div>

        <div class="side">
          {side_content}
        </div>
      </div>
    <div class="below">
      {below_content}
    </div>
  </div>
</body>
</html>
"""


plainhero = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .content-section {
            padding: 40px;
            background-color: #ffffff;
        }

        .content-title {
            font-size: 28px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 15px;
        }

        .content-text {
            color: #333;
            line-height: 1.8;
            font-size: 16px;
        }

        .content-text h2 {
            font-size: 22px;
            font-weight: 600;
            color: #1a1a1a;
            margin-top: 25px;
            margin-bottom: 15px;
            border-left: 4px solid #007bff;
            padding-left: 15px;
        }

        .content-text h3 {
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-top: 18px;
            margin-bottom: 12px;
            padding-left: 10px;
        }

        .content-text h4 {
            font-size: 16px;
            font-weight: 600;
            color: #34495e;
            margin-top: 15px;
            margin-bottom: 10px;
        }

        .content-text p {
            margin-bottom: 15px;
        }

        .content-text ol {
            margin-left: 20px;
            margin-bottom: 15px;
        }

        .content-text li {
            margin-bottom: 10px;
            color: #444;
        }

        .content-text ul {
            margin-left: 20px;
            margin-bottom: 15px;
        }

        .content-text ul li {
            margin-bottom: 8px;
            color: #444;
        }

        .content-text strong {
            color: #1a1a1a;
            font-weight: 600;
        }

        /* Special styled boxes */
        .highlight-box {
            background-color: #e7f3ff;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            color: #004085;
        }

        .evidence-gap {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            font-style: italic;
            color: #856404;
        }

        .warning-box {
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            color: #721c24;
        }

        .data-correction {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            color: #155724;
        }

        .section-divider {
            border: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, #ddd, transparent);
            margin: 25px 0;
        }

        /* Table styles */
        .table-wrapper {
            overflow-x: auto;
            margin: 20px 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }

        table th {
            background-color: #007bff;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }

        table td {
            border-bottom: 1px solid #ddd;
            padding: 12px;
        }

        table tr:hover {
            background-color: #f5f5f5;
        }

        .old-value {
            text-decoration: line-through;
            color: #999;
            font-size: 13px;
        }

        @media (max-width: 768px) {
            .content-section {
                padding: 20px;
            }

            .content-title {
                font-size: 22px;
            }

            .content-text {
                font-size: 14px;
            }
        }
    </style>
</head>

<body>
    <div class="container">
        <!-- Content Section -->
        <div class="content-section">
            <div class="content-text">
                {content}
            </div>
        </div>
    </div>
</body>

</html>"""


plaindual = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        /* Content section with title and columns */
        .content-section {
            padding: 40px;
            background-color: #ffffff;
        }

        .content-title {
            font-size: 28px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 15px;
        }

        /* Two column layout */
        .columns {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-top: 25px;
        }

        .column {
            color: #333;
            line-height: 1.8;
            font-size: 16px;
        }

        .column h2 {
            font-size: 22px;
            font-weight: 600;
            color: #1a1a1a;
            margin-top: 25px;
            margin-bottom: 15px;
            border-left: 4px solid #007bff;
            padding-left: 15px;
        }

        .column h2:first-child {
            margin-top: 0;
        }

        .column h3 {
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-top: 18px;
            margin-bottom: 12px;
            padding-left: 10px;
        }

        .column h4 {
            font-size: 16px;
            font-weight: 600;
            color: #34495e;
            margin-top: 15px;
            margin-bottom: 10px;
        }

        .column p {
            margin-bottom: 15px;
        }

        .column ol {
            margin-left: 20px;
            margin-bottom: 15px;
        }

        .column li {
            margin-bottom: 10px;
            color: #444;
        }

        .column ul {
            margin-left: 20px;
            margin-bottom: 15px;
        }

        .column ul li {
            margin-bottom: 8px;
            color: #444;
        }

        .column strong {
            color: #1a1a1a;
            font-weight: 600;
        }

        /* Special styled boxes */
        .highlight-box {
            background-color: #e7f3ff;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            color: #004085;
        }

        .evidence-gap {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            font-style: italic;
            color: #856404;
        }

        .warning-box {
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            color: #721c24;
        }

        .data-correction {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            color: #155724;
        }

        .section-divider {
            border: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, #ddd, transparent);
            margin: 25px 0;
        }

        /* Table styles */
        .table-wrapper {
            overflow-x: auto;
            margin: 20px 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }

        table th {
            background-color: #007bff;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }

        table td {
            border-bottom: 1px solid #ddd;
            padding: 12px;
        }

        table tr:hover {
            background-color: #f5f5f5;
        }

        .old-value {
            text-decoration: line-through;
            color: #999;
            font-size: 13px;
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .content-section {
                padding: 20px;
            }

            .content-title {
                font-size: 22px;
            }

            .columns {
                grid-template-columns: 1fr;
                gap: 25px;
            }

            .column {
                font-size: 14px;
            }
        }
    </style>
</head>

<body>
    <div class="container">
        <!-- Content Section with Title and Two Columns -->
        <div class="content-section">
            <div class="columns">
                <div class="column">
                    {content_1}
                </div>
                <div class="column">
                    {content_2}
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""

# export templates dict
templates = {
    "hero": hero,
    "dual": dual,
    "embedded": embedded,
    "plainhero": plainhero,
    "plaindual": plaindual,
    "1": hero,
    "2": dual,
    "3": embedded,
    "4": plainhero,
    "5": plaindual,
}