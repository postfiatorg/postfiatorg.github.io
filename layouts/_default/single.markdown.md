# {{ .Title }}

{{ with .Date }}Published: {{ .Format "2006-01-02" }} · Post Fiat Research{{ end }}
{{ with .Summary }}
{{ . }}
{{ end }}
Canonical: {{ .Permalink }}
Markdown source of the page above. Other formats and the research blog index: https://postfiat.org/blog/

---

{{ .RawContent }}
