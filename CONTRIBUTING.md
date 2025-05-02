hyperglass is primarily maintained by me, [Matt Love](https://github.com/thatmattlove). This was my first ever open source application, and as such, it's kind of my "baby". When I first started writing hyperglass, I knew _nothing_ about development, Python, JavaScript/TypeScript, or GitHub. I was a network engineer trying to solve a problem and learn a few things while I was at it.

Because I've been solo-maintaining and building hyperglass since around April 2019, I've become pretty particular about things that might seem trivial to someone just trying to help out. While I welcome development contributions, please don't be offended if pull requests are denied, if I request things to be done a certain way, or if I integrate something similar to your changes separately from your PR. To help understand why, here are some of the development design goals for hyperglass:

- **Pristine code quality**
  - [Black](https://github.com/python/black) formatting for Python.
  - Strict adherence to ESLint/Prettier configs for frontend code.
  - _ZERO_ linting errors.
  - Linting exceptions only used when there is _no other way_, and should be accompanied with comments about why there is no other way.
- **No hard-coding**
  - Anything visible to the end-user _must_ be customizable by the administrator. If it's not, or can't be, leave code or PR comments as to why.
  - This includes things like timeouts, error messages, etc.
- **Mobile & Accessible**
  - All UI element must be available on both desktop and mobile devices.
  - UI must achieve a 100 Lighthouse/PageInsights score for accessibility.
- **IPv6 Support**
  - Any new device support must include IPv6 commands.
  - All frontend and backend code must support IPv6, both for running the application and processing queries.
