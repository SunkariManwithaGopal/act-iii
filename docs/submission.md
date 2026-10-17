**Title**  
Restock Copilot Lite

**Short Description**  
A tool that tells small shops what to reorder and why, using transparent forecasting and AMD-powered plain-English explanations.

**Long Description**  
Small shop owners struggle with inventory: overstocking ties up cash, while understocking loses sales. Restock Copilot Lite solves this by analyzing historical sales to recommend precise reorder quantities. We built a transparent forecasting engine using two non-language-model methods (a 4-week baseline and a seasonal trend adjuster). We proved its value via an 8-week replay simulation, measuring actual lost sales and leftover stock. Crucially, we integrated an AMD Token Factory model to translate the raw numerical output into plain-English explanations for the buyer. The language model does not forecast; it only explains. Our results show a forecast error of `[SEASONAL_ERROR]` and `[SEASONAL_LOST]` lost units under the seasonal method. Limits include the use of simulated stock and historical public data (UCI Online Retail II). Next steps include integrating real-time supplier lead times.

**Technology Tags**  
Python, FastAPI, Pandas, AMD Token Factory, Docker, UCI Dataset, Time-Series Forecasting, OpenAI-Compatible API
