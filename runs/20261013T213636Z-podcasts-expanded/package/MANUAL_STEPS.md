# Manual steps remaining for run 20261013T213636Z-podcasts-expanded

Preparing this package does not render videos or publish anything.

1. Produce each video in Google Vids or HeyGen from package/NN-video-script.md (Visual/On-screen text/Narration per scene); an avatar is optional. Export MP4.
2. Publish each package/NN-article.md on Substack with shareable (free) access; keep the Sources section and the AI-assistance line.
3. Upload each video to YouTube (public or unlisted) using package/NN-youtube-description.txt as the description; add the Substack link to it.
4. Add the YouTube link to the corresponding Substack article.
5. Fill substack_url and youtube_url for every piece in package/publication_links.json; rerun `bash run.sh --package RUN_DIR` to refresh the summary (links are preserved).
