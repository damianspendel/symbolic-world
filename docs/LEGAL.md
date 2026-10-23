# Legal statement

The Symbolic World: a knowledge graph of C. G. Jung's *Collected Works*
Date: 2026-07-27. Figures as of the v2.1.0 freeze, 2026-10-23.

This statement sets out what the project publishes and the legal basis for it.

## 1. What the project contains

The Symbolic World is a scholarly knowledge graph of C. G. Jung's *Collected Works* (CW), built by Damian Spendel with AI collaborators. It has three parts: a public web application (symbolicworld.observer), a dataset (`seed.json`), and a research paper (`docs/PAPER.md`).

The dataset contains 3,562 references at release v2.1.0, and it grows under the same rules. Each reference includes:

- a verbatim quotation of at most 25 words from a single CW paragraph
- the CW volume and paragraph number (§)
- a Bollingen edition page number
- scholarly metadata (claim type, verification provenance)

The project does not contain the text of the *Collected Works*. It does not distribute the full source texts, commit them to this repository, or serve them from the web application. It publishes only the short quotations, § numbers, and page numbers described above.

The graph itself (its nodes, relations, and claim typing) is original analytical work. It describes and organizes claims about the CW and does not reproduce them. Its closest analogues are an index, a concordance, or a scholarly apparatus.

## 2. Copyright status of the underlying works

The English translations of the *Collected Works* (translated by R.F.C. Hull, Bollingen Series XX, published by Princeton University Press and, in the UK, Routledge) are under copyright. This project treats them as such.

Jung's German originals have a separate status: Jung died in 1961, so in life-plus-70 jurisdictions the German originals begin entering the public domain from 2032. We do not rely on this and make no claim that any of the underlying material is in the public domain today. The Hull translations carry their own copyright, and that copyright is current. Every quotation in this dataset comes from the copyrighted English translations.

## 3. Legal basis: quotation for scholarship

The project relies on the long-established quotation and fair-use/fair-dealing exceptions that permit short, attributed excerpts for scholarship, criticism, and review.

<!-- vale off -->
United States: fair use (17 U.S.C. § 107). We assess the first three factors here. The next section takes up the dataset as a whole.
<!-- vale on -->

- Purpose and character: nonprofit scholarship and criticism. Each quotation anchors and verifies a specific analytical claim, which is the ordinary function of a citation.
- Nature of the work: the CW are scholarly works in print, and quotation for scholarly discussion of published works is central to what the exception protects.
- Amount and substantiality: each excerpt is at most 25 words, individually necessary to identify and verify the paragraph a claim rests on. No excerpt captures the "heart" of a volume.

United Kingdom and European Union. UK law (CDPA s. 30) permits fair dealing with a work for quotation, criticism, and review, and the EU InfoSoc Directive (art. 5(3)(d)) provides an equivalent quotation exception. Our quotations meet the usual conditions. Princeton and Routledge have published the works, each quotation names its source (volume, paragraph, page), the extent is no more than the purpose requires, and the use is for a genuine scholarly purpose.

Switzerland. The project is run from Switzerland, where the quotation right is in the Copyright Act (URG art. 25). It permits quotation from a published work when the quotation serves to explain, to refer, or to illustrate, and the purpose justifies its extent. The person quoting must mark the quotation, name its source, and name the author where the source does. The Federal Supreme Court adds that a quotation must have a link in content to the text that cites it and must not carry independent or main significance of its own (BGE 131 III 480). The atlas marks each quotation as a quotation and gives its volume, paragraph, and page. Each sits under an authored claim about how two concepts relate, and it is there so that a reader can check that claim against the paragraph.

## 4. The dataset as a whole

Any single 25-word quotation is plainly within quotation norms. A dataset of 3,562 such quotations is an aggregation, and this section addresses it as one.

- Scale: 3,562 quotations of at most 25 words come to 56,205 words, a mean of 15.8 words each. They are drawn from the nine volumes mined so far, which hold about 1.24 million words, so the quotations are 4.5% of those volumes. The highest share in any one volume is 7.4% (CW 8). The *Collected Works* run to roughly twenty volumes, so the share of the whole is lower.
- Non-substitutive: the quotations are discontinuous fragments selected because they anchor citations, not because they represent the work's expressive interest. Read together they do not form readable text and could not serve anyone as a substitute for reading Jung.
- Toward the books: if anything, the dataset sends readers to Jung. A quotation of 25 words or fewer cannot stand in for its paragraph, and each one gives the volume, paragraph, and page where the reader finds the full passage in the printed edition.
- Function: the dataset works as a concordance, a finding aid that tells a reader where in the CW a claim rests and gives enough verbatim text to verify the match. Paragraph (§) numbers and page numbers are facts, and copyright does not protect facts.

## 5. Takedown and contact

We intend to act in good faith toward the rights holders. If any rights holder, including Princeton University Press, Routledge, or the Jung estate, believes any quotation in this dataset exceeds what the quotation exceptions permit, we will review the concern promptly and, where warranted, shorten or remove the contested quotations. Rights holders can raise a concern on the repository's issue tracker or at the project's published contact address.

## 6. Licensing of the project's original content

- Code: MIT License.
- Dataset (original content): the graph structure, relations, claim typing, and scholarly metadata are available under CC BY 4.0.
- Quotations: both license grants exclude the verbatim CW quotations. They remain under the copyright of their respective rights holders and appear here in reliance on the quotation and fair-use exceptions described above. Reusers of the dataset must make their own assessment of the quotations for their own use.

The repository's NOTICE file states these terms, and the LICENSE file carries the MIT text alone.

## 7. AI disclosure

AI models (Claude Opus and Fable, Anthropic; Gemini, Google) carried out extraction and verification under human direction. A mechanical check matched every quotation against the source texts as a letter-normalized, in-order, near-contiguous excerpt with bounded elisions. So far AI models have performed the semantic verification of claims, with human verification of a reference sample planned and disclosed as outstanding in the accompanying paper.

## 8. Disclaimer

This statement is the project's good-faith position, prepared without legal counsel. It is not legal advice, and it does not bind anyone else's assessment: rights holders may take a different view, and the law of quotation varies by jurisdiction. We publish it so that others can check our reasoning and correct it.
