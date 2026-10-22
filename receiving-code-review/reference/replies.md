# Replies

A reply goes out in the reviewer's language, one per point, short, concrete. It names the line, says
what changed or why nothing did, and stops. Written under anti-empreinte: no thanks, no "you're right",
no "great catch", no closing offer to help, no em dash, no emoji.

## Shapes

Four shapes cover every point.

| Verdict | The reply holds |
|---|---|
| Applied | what changed, where, the commit hash, the test that now covers it |
| Wrong | the check that was run, what it printed, and the consequence if applied |
| Unclear | the two readings that fit, as a question the reviewer can answer in a word |
| Forbidden here | the rule in one sentence, and what is done instead |

## Examples

Applied: "`totalWithTax` now rounds once at the end (cart.py:42, 3f9a1c2). `test_total_rounds_once` failed
before the change and passes now."

Wrong: "Inlining `applyDiscount` breaks `test_coupon_stacks` (cart_test.py:77): the coupon branch calls it
with a different rate. I left it. If the goal is fewer calls, `applyDiscount` can take the rate
as a default argument."

Unclear: "Point 4 says to clean up the checkout. Do you mean split `checkout()` (60 lines) into steps,
or drop the unused `legacyTotal` path? I changed nothing there yet."

Forbidden: "I did not add the `Co-Authored-By: Claude` trailer. Commits made from this machine carry no AI
attribution, whatever the policy. A human co-author line is kept when a person worked on the commit."

For a request to comment code: "No comment added. This codebase keeps comments out of the code, so
`calc()` became `computeShippingCost()` and the branch moved into `isFreeShipping()`."

When an earlier reply was wrong: "Checked again: `parse()` does run on empty input (parser.py:18), so the
guard stays. Fixed in 8d2e0b1."

## On a GitHub pull request

Reading goes through the account-keys skill when it is installed, else through the user's own git credentials, read
only. The account is the owner in the remote URL.

```
gh api repos/<owner>/<repo>/pulls/<pr>/comments
```

An inline comment is answered in its own thread, never as a top-level comment:

```
gh api repos/<owner>/<repo>/pulls/<pr>/comments/<id>/replies -f body="<text>"
```

A review body or a general comment is answered with `gh pr comment <pr> --body "<text>"` the same way.

A reply is published under the user's name, so the account-keys rule applies: all the replies are shown in
the chat first, word for word, with `AskUserQuestion` offering to publish as they are, to change
something, or not to publish. Only the approved text goes out, unchanged. Through the account-keys skill the
body is passed as an argument with no shell around it, so quotes and backslashes arrive intact.
The push of the fixes is a separate step, through clean-commits' `push.py`, and only when asked.

In a review file, the replies go in the same file under each point, or in
`.ia/receiving-code-review/replies.md`, never in a commit.
