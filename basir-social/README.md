# Basir Yazd – public, free visual-media generator

This subfolder is an independent asset-only part of the Basir Yazd content
pipeline. It can run on GitHub Actions without third-party subscriptions.

## What runs unattended

- Creates 14 daily **1080×1920** vertical JPG story graphics.
- Uses pre-reviewed, evergreen Persian advice about charity, volunteering,
  kindness, privacy, and Friday Mahdavi good deeds.
- Prints **قرارگاه جهادی حضرت بقیةالله (عج)** and **@basiryazd** on each image.
- Generates a manifest and a reusable public URL for each story:
  `https://raw.githubusercontent.com/basiryazd/rozeh-manager/main/basir-social/public_media/story-YYYY-MM-DD.jpg`
- GitHub Actions runs every day (at about 20:15 Iran time), creates images
  and pushes the files to the repository's public branch. A push to main
  also refreshes the assets.
- Marks designs as educational illustrations, not photographs/reports from
  actual charity fieldwork.

## What this does NOT do

This asset workflow **does not publish to Instagram or Facebook**. It
generates and hosts the media publicly for the separate **authorized** social
publisher. GitHub Actions status 'success' does *not* mean a social post was
published. It does not read Eitaa, use or bypass Metricool, or use unofficial
Instagram/Facebook logins.

### Integration – social publisher

Only after the images exist on the public main branch, a legitimate publisher
can use the URLs in the JSON manifest:

- Instagram Story: `instagramData.type = STORY`
- Facebook Story: `facebookData.type = STORY`
- Caption: blank (story text is already on the image)
- Timezone: `Asia/Tehran`
- `autoPublish: true` where supported
- Maintain a deduplication ledger and respect each provider's subscription
  quotas. The existing Metricool Free integration is quota-limited.
- Direct Meta Graph publishing requires the publisher's official authorization
  and credentials; do not activate it prematurely.

## Safety requirements

Never turn a suggested charitable activity into a false factual report. Real
Eitaa stories/photos must be checked for consent, privacy, and dress
requirements. Do not decorate genuine reportage with invented covers or
people; preserve originals as provided. Do not publish a private photograph
in this public repository.

GitHub workflow: `.github/workflows/basir-social-media.yml`
