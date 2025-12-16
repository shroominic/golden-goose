# Golden Goose

A development bot on nostr that implements whatever you want.

This is a goose coding agent nostr bot.

## Usage

You can use it by publishing a nostr kind 1 event starting with `nostr:npub1aa9fdlcpehxsjenqmqx3ytj78x6ctp07p8vqh04pt0xx0xqru3mswxfw72`, which is equivalent to tagging `@goldenGoose` in the beginning of the note.

## Status

**Note: This is not yet production ready.**

We urgently need to implement:

- [ ] Hardening (running goose inside docker)
- [ ] Payment handling: keeping a user balance of how much each user has zapped the bot to pay the AI cost from these zaps.
- [ ] rate limiting using balances or social graph

Other improvements:

- [ ] Follow up messages: the bot should be able to follow up on the user's request and respond considering relevant context.
- [ ] each user should be able to adjust their desired model or custom instructions
