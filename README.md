# paid-app-charts

发达国家（美/英/法/日/韩/澳 + 德/加/荷/瑞典）iOS **付费榜**看板，带「收费 × 智能体化」短名单。

## 查看

GitHub Pages 开启后打开站点根目录 `index.html`。

## 数据

- `data/latest.json` — 榜单明细、跨国共现、机会短名单
- `scripts/refresh.py` — 重新拉取 Apple RSS / Marketing Tools

```bash
python3 scripts/refresh.py
```

## 口径

只看 Paid charts；智能体化讨论以付费应用榜为主，强 IP 游戏与代理工具慎碰。
