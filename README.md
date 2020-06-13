# NUS-Cap-Target
NUS Cap Target is a telegram bot which primarily helps students calculate the average Cumulative Average Point (CAP) required in order to attain that ideal graduation CAP. This was developed to complement the NUS SU Calculator, specially catered for those who have no other modules to S/U (senior batches/graduating students). The bot is stable, fast and accurate. It is officially pushed out for use on 04/06/2020 and subsequently 08/06/2020 in preparation for the release of results on 09/06/2020. NUS Cap Target has received an overwhelming 3000+ users till date. Bot address: https://t.me/nusacadplanCAP_bot


## Installation
```bash
pip install logging
pip install inflect
pip install telegram
```

## Usage
```python
import logging
import inflect
import os
import telegram

PORT = int(os.environ.get('PORT', < Port Number > ))
bot = telegram.Bot(token= < API Key >)

updater = Updater(
        < API Key > , use_context=True)
      
#For webhook
updater.start_webhook(listen= < Listen Address >,
                          port=int(PORT),
                          url_path= < API Key >)

updater.bot.setWebhook( < Server Name > +
                           < API Key > )
```
