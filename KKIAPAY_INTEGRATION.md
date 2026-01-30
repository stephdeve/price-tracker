# KKiapay Integration

This application integrates with KKiapay for premium subscription payments.

## Environment Variables

Add the following to your `.env` file (backend):

```bash
# KKiapay Payment Configuration (Free for Benin/Africa)
MAIL_MAILER=smtp
MAIL_HOST=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=f22e142a1e8719
MAIL_PASSWORD=fc759e0c387490
MAIL_FROM_ADDRESS="hello@example.com"
MAIL_FROM_NAME="${APP_NAME}"

#Kkiapay
KKIAPAY_PUBLIC_KEY=d1e321f0a85711f0a47f0581fe5152d6
KKIAPAY_PRIVATE_KEY=tpk_d1e34900a85711f0a47f0581fe5152d6
KKIAPAY_SECRET=tsk_d1e37010a85711f0a47f0581fe5152d6
KKIAPAY_MODE=sandbox
KKIAPAY_CALLBACK_URL=https://dd4f41d82647.ngrok-free.app/payment/callback 

# Pricing (XOF - Franc CFA)
PREMIUM_MONTHLY_PRICE_XOF=1000
PREMIUM_YEARLY_PRICE_XOF=10000

# Set to True for sandbox mode (development)
DEBUG=True
```

## Features Implemented

- Server-side transaction verification via KKiapay API before activating premium
- Support for monthly and annual subscription plans
- Frontend button shows spinner and remains disabled during payment
- Webhook endpoint for asynchronous payment notifications
- Automatic redirect to pricing after login with upgrade flow
- Dynamic KKiapay SDK loading

## API Endpoints

- `GET /api/v1/payments/config` - Returns KKiapay config and pricing
- `POST /api/v1/payments/kkiapay/confirm` - Confirms payment with server-side verification
- `POST /api/v1/payments/kkiapay/webhook` - Webhook for KKiapay notifications

## Security Notes

- Never expose private keys or secrets in frontend code
- Server-side verification prevents tampered frontend requests
- Webhook signature verification should be implemented based on KKiapay's documentation
